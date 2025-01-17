# coding=utf-8
from flask import Blueprint, render_template, request, flash, redirect, get_flashed_messages, message_flashed
from flask.ext.login import (current_user, login_required)
from mongoengine import Q as db_query
from mongoengine import ValidationError
from datetime import datetime

from resumeme.utils.controllers import send_mail

import models
import constants as CONSTANTS
import utils

feedback = Blueprint('feedback', __name__, template_folder='templates')


# Show thank you and saved message for review submission
#
@feedback.route('/review/<state>')
@login_required
def test(state):
    flash("Votre critique a été enregistré.")
    if state == "saved":
        templateData = {
            'first_message': "Merci d’avoir noté votre feedback !",
            'second_message': ""
        }
    elif state == 'saved_and_sent':
        templateData = {
            'first_message': "Merci d’avoir noté votre feedback !",
            'second_message': "Et merci aussi de supporter votre bénévole !"
        }
    else:
        return render_template('404.html')
    return render_template('feedback/review_thank_you.html', **templateData)


# List of Resume or Feedback seen based on role
#
@feedback.route('/feedback')
@login_required
def feedback_main():
    user = models.User.objects.with_id(current_user.id)
    if user.role == "jobseeker":
        user_resume_list = models.Resume.objects(user=current_user.id)
        user_feedback_list = models.Feedback.objects(user=current_user.id)
        templateData = {
            'resume': user_resume_list,
            'feedback': user_feedback_list
        }
        return render_template('feedback/seeker.html', **templateData)
    elif user.role == "volunteer":

        user_resume_list = models.Resume.objects(
            db_query(user__ne=current_user.id) &
            db_query(lock=False)
        )

        templateData = {
            'resume': user_resume_list
        }
        return render_template('feedback/volunteer.html', **templateData)
    else:
        return render_template('404.html')


# Create New Feedback
#
@feedback.route("/feedback/<resume_id>/create", methods=["GET", "POST"])
@login_required
def volunteer_add_feedback(resume_id):
    resume_requested = models.Resume.objects().with_id(resume_id)
    if request.method == "POST" and resume_requested.lock is False:
        try:
            # Tells the feedback display page that the feedback was freshly created and saved.
            state = "saved"
            created = datetime.now()
            current_resume = models.Resume.objects().with_id(resume_id)
            feedback = models.Feedback()
            feedback.last_updated = created

            feedback.first_section = models._Section()
            feedback.second_section = models._Section()
            feedback.third_section = models._Section()
            feedback.fourth_section = models._Section()
            feedback.fifth_section = models._Section()

            feedback.resume = current_resume

            feedback.first_section.name = CONSTANTS.FIRST_SECTION
            feedback.first_section.rating = request.form.get('rating_1')
            feedback.first_section.content = request.form.get('content_1')
            feedback.second_section.name = CONSTANTS.SECOND_SECTION
            feedback.second_section.rating = request.form.get('rating_2')
            feedback.second_section.content = request.form.get('content_2')
            feedback.third_section.name = CONSTANTS.THIRD_SECTION
            feedback.third_section.rating = request.form.get('rating_3')
            feedback.third_section.content = request.form.get('content_3')
            feedback.fourth_section.name = CONSTANTS.FOURTH_SECTION
            feedback.fourth_section.rating = request.form.get('rating_4')
            feedback.fourth_section.content = request.form.get('content_4')
            feedback.fifth_section.name = CONSTANTS.FIFTH_SECTION
            feedback.fifth_section.rating = request.form.get('rating_5')
            feedback.fifth_section.content = request.form.get('content_5')

            feedback.validate()

            feedback.resume.update(lock=True)

            # associate feedback to resume owner
            feedback.user = feedback.resume.user

            # associate it to volunteer
            volunteer = models.User.objects.with_id(current_user.id)
            feedback.volunteer = volunteer
            feedback.save()

            # push feedback onto resume feedback_list reference list
            models.Resume.objects(id=resume_id).update_one(push__feedback_list=feedback)
            current_resume.save()

            return redirect('/feedback/%s/%s/%s' % (feedback.resume.id, feedback.id, state))

        except ValidationError as e:
            print "Error:", e
            flash('Remplir tous les champs')
            template_data = {
                'title': 'Donner feedback',
                'content': None,
                'resume': models.Resume.objects().with_id(resume_id)
            }
            return render_template('feedback/edit.html', **template_data)

    elif resume_requested.lock is True:
        return render_template('404.html')

    else:
        template_data = {
            'title': 'Donner Feedback',
            'content': None,
            'resume': models.Resume.objects().with_id(resume_id)
        }
        return render_template('feedback/edit.html', **template_data)


# View of Resume with Feedback and whether it needs a flash saying
# saved or not.
#
@feedback.route('/feedback/<resume_id>/<feedback_id>/<state>')
@login_required
def entry_page(resume_id, feedback_id, state="view"):
    # get class resume entry with matching slug
    resume = models.Resume.objects().with_id(resume_id)
    feedback = models.Feedback.objects().with_id(feedback_id)

    if resume and feedback:
        # Display this only when the feedback is freshly saved and not when it is just being viewed.
        if state == "saved":
            flash('Feedback has been saved')

            subject = "[RevueCV] Nouveau feedback pour " + resume.title + " disponible"
            host_url = request.url_root
            user = resume.user

            if user.active:
                send_mail(subject, user.email, 'new_feedback',
                          user=user, url=host_url, resume=resume)

        else:
            feedback.viewed = True
            feedback.save()

        templateData = {
            'title': 'Votre Feedback',
            'resume': resume,
            'feedback': feedback
        }

        return render_template('feedback/view.html', **templateData)

    else:
        return render_template('404.html')


# Give Review of feedback
#
@feedback.route('/feedback/<resume_id>/<feedback_id>/review', methods=['GET', 'POST'])
@login_required
def review(resume_id, feedback_id):
    resume = models.Resume.objects().with_id(resume_id)
    feedback = models.Feedback.objects().with_id(feedback_id)

    # If model is old
    if hasattr(feedback, "version") is False:
        flash(utils.get_message_text("sorry_old_model"))
        return redirect('/feedback')

    if request.method == "POST" and feedback.review_lock is False:
        # Takes the Seeker's input to create the entry in the database
        try:
            feedback.first_question = request.form.get('question_1')
            feedback.second_question = request.form.get('question_2')
            feedback.third_question = request.form.get('question_3')

            feedback.first_section.review = request.form.get('section_1')
            feedback.second_section.review = request.form.get('section_2')
            feedback.third_section.review = request.form.get('section_3')
            feedback.fourth_section.review = request.form.get('section_4')
            feedback.fifth_section.review = request.form.get('section_5')

            feedback.validate()

            feedback.update(review_lock=True)
            feedback.save()

            message_to_display = "saved"
            if request.form.get('thank_you') == CONSTANTS.CHOICE_ONE:
                subject = "[RevueCV] Merci !"
                host_url = request.url_root
                user = feedback.volunteer
                send_mail(subject, user.email, 'thank_you',
                          user=user, url=host_url, resume=resume)
                message_to_display = "saved_and_sent"
                feedback.update(thank_you_message=True)
                feedback.save()
            return redirect('/review/%s' % message_to_display)

        except ValidationError as e:
            print "Erreur:", e
            flash("Il y a eu une erreur avec votre soumission. Veuillez réessayer.")
            return redirect('/feedback/%s/%s/review' % (feedback.resume.id, feedback.id))


    else:
        # Shows the survey page (review)
        templateData = {
            'title': 'Noter votre feedback',
            'resume': resume,
            'feedback': feedback
        }
        return render_template('feedback/review.html', **templateData)

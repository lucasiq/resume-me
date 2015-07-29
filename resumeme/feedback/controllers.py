from flask import Blueprint, render_template, request, flash, redirect
from flask.ext.login import (current_user, login_required)
from mongoengine import Q as db_query
from mongoengine import ValidationError

import models
import constants as CONSTANTS

feedback = Blueprint('feedback', __name__, template_folder='templates')


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
        user_resume_list = models.Resume.objects(db_query(user__ne=current_user.id) & db_query(lock=False))
        templateData = {
            'resume': user_resume_list,
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
            feedback = models.Feedback()
            feedback.first_section = models._Section()
            feedback.second_section = models._Section()
            feedback.third_section = models._Section()
            feedback.fourth_section = models._Section()
            feedback.fifth_section = models._Section()

            feedback.resume = models.Resume.objects().with_id(resume_id)

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
            feedback.save()

            return redirect('/feedback/%s/%s/%s' % (feedback.resume.id, feedback.id, state))

        except ValidationError as e:
            print "Error:", e
            flash('Fill out all fields')
            template_data = {
                'title': 'Give Feedback',
                'content': None,
                'resume': models.Resume.objects().with_id(resume_id)
            }
            return render_template('feedback/edit.html', **template_data)

    elif resume_requested.lock is True:
        return render_template('404.html')

    else:
        template_data = {
            'title': 'Give Feedback',
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
        else:
            feedback.viewed = True
            feedback.save()

        templateData = {
            'title': 'Your Feedback',
            'resume': resume,
            'feedback': feedback
        }

        return render_template('feedback/view.html', **templateData)

    else:
        return render_template('404.html')


$('#file').bind('change', function () {
    size = this.files[0].size / 1024 / 1024;
    submit = $('#submitfile');

    if (size > 1) {
        submit.prop('disabled', true);
        alert('Le fichier que vous attachez est plus gros que ce qui est autorisé. Essayez de joindre un fichier de taille inférieure.');
    } else if (size < 0.01) {
        alert('Nous avons détecté que la taille de ce fichier est inférieure à 10 octets. Êtes-vous sûr de télécharger le bon fichier?');
    } else {
        submit.prop('disabled', false);
    }

});

$(function () {
    // instantiate the addressPicker suggestion engine (based on bloodhound)
    var addressPicker = new AddressPicker({
        autocompleteService: {types: ['(cities)'], componentRestrictions: {country: 'US'}}
    });

    // instantiate the typeahead UI
    $('#location').typeahead(null, {
        displayKey: 'description',
        source: addressPicker.ttAdapter()
    });
});

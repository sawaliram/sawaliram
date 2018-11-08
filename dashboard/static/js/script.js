
function addQuestion() {
    $('.add-question-button').click(function(event) {
        event.preventDefault();

        var last_question_card = $('.question-card').last();
        var new_question_card = last_question_card.clone();
        var last_question_number = parseInt(last_question_card.find('.question-number').text());

        new_question_card.find('.question-number').text(last_question_number + 1);
        new_question_card.find('.delete-question-button').css('display', 'block');

        new_question_card.insertAfter(last_question_card);
        deleteQuestion();
    });
}

function deleteQuestion() {
    $('.delete-question-button').click(function(event) {
        
        $(this).closest('.question-card').hide('normal', function() {
            $(this).closest('.question-card').remove();
        });

        reserializeQuestionCards();
    });
}

function reserializeQuestionCards() {
    var serial_number = 1;

    $('.question-card').each(function() {
        $(this).find('.question-number').text(serial_number);
        serial_number++;
    });
}

function displayNameOfSelectedFile() {
    
    $('#excelFileBrowser').change(function() {
        var file_name = $(this).val().replace('C:\\fakepath\\', '');
        $(this).next('.custom-file-label').text(file_name);
    });
}

function togglePublishedInformationFormGroups() {

    $('input[type=radio][name=published]').change(function() {
        if (this.value == 'True') {
            $('input[type=text][name=published-source]').prop('required', true);
            $('.published-information').show(300);
            $('input[type=text][name=area]').removeAttr('required');
            $('input[type=text][name=state]').removeAttr('required');
            $('select[name=context]').removeAttr('required');
            $('.not-required-if-published').hide(300);
        }
        else {
            $('input[type=text][name=published-source]').removeAttr('required');
            $('.published-information').hide(300);
            $('input[type=text][name=area]').prop('required', true);
            $('input[type=text][name=state]').prop('required', true);
            $('select[name=context]').prop('required', true);
            $('.not-required-if-published').show(300);
        }
    });
}

addQuestion();
displayNameOfSelectedFile();
togglePublishedInformationFormGroups();
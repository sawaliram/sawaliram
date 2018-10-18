
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

addQuestion();
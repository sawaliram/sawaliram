
// ======== GENERAL FUNCTIONS ======== 
// JS functions that must be called for every page

function toggleNavbarMenu() {
    $(document).ready(function() {
        $('.navbar-menu-toggle').click(function() {
            $('.navbar-menu').addClass('navbar-menu-open');
            $('.menu-background').addClass('darken');
        });
        $('.navbar-menu-close').click(function() {
            $('.navbar-menu').removeClass('navbar-menu-open');
            $('.menu-background').removeClass('darken');
        });
    });
}

function toggleUserMenu() {
    $(document).ready(function() {
        $('.user-menu-button').click(function() {
            $('.user-menu').addClass('open');
            $('.menu-background').addClass('darken');
        });
        $('.user-menu-close').click(function() {
            $('.user-menu').removeClass('open');
            $('.menu-background').removeClass('darken');
        });
    });
}

function closeMenusOnClickingDarkbackground() {
    $('.menu-background').click(function() {
        $('.navbar-menu').removeClass('navbar-menu-open');
        $('.user-menu').removeClass('open');
        $(this).toggleClass('darken');
    });
}

function resizeMainLogoOnScrollDown() {
    $(window).scroll(function() {
        if ($(window).scrollTop() > 100) {
            $('#mainLogo').css('width', '190px');
        }
        else {
            $('#mainLogo').css('width', '250px');
        }
    });
}

function highlightSelectedVolunteerOption() {
    $('.volunteer-option input:checkbox').change(function() {
        if(this.checked) {
            $(this).parent('.volunteer-option').addClass('selected');
        }
        else {
            $(this).parent('.volunteer-option').removeClass('selected');
        }
    });
}

function openVolunteerOptionDialog() {
    $('.volunteer-option input:checkbox').change(function() {
        if(this.checked) {
            $(this).parent('.volunteer-option').find('.volunteer-dialog textarea').prop('required', true);
            $(this).parent('.volunteer-option').find('.volunteer-dialog').show(300);
        }
        else {
            $(this).parent('.volunteer-option').find('.volunteer-dialog textarea').prop('required', false);
            $(this).parent('.volunteer-option').find('.volunteer-dialog').hide(300);
        }
    });
}

function togglePlaintextPassword() {
    $('.password-plaintext i').click(function() {
        if ($(this).hasClass('fa-eye-slash')) {
            $(this).removeClass('fa-eye-slash');
            $(this).addClass('fa-eye');
        }
        else {
            $(this).removeClass('fa-eye');
            $(this).addClass('fa-eye-slash');
        }

        $('.password-plaintext').toggleClass('hidden');
    });
}

function copyPasswordToPlaintextArea() {
    $('.password-field').on('input', function() {
        $('.password-plaintext span').text($(this).val());
    });
}


// ======== PAGE SPECIFIC FUNCTIONS ========
// These functions are called only on specific pages

// ======== OLDER SCRIPTS ========
// These functions will either be phased out or moved
// into the general or specific functions sections above

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

function toggleOtherOrganisationTextBox() {

    $('#organisationDropDown').change(function() {
        if (this.value == 'other') {
            $('.other-organisation-textbox').show(300)
        }
        else {
            $('.other-organisation-textbox').hide(300)
        }
    });
}

function setupQuillEditor() {

    var quill = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: '#toolbar'
        }
    });

    $('.rich-text-form').submit(function(e) {
        $('[name="rich-text-content"]').val(quill.root.innerHTML);
    });
}

// ======== CALL GENERAL FUNCTIONS ========

toggleNavbarMenu();
toggleUserMenu();
closeMenusOnClickingDarkbackground();

if (window.matchMedia("(min-width: 576px)").matches) {
    resizeMainLogoOnScrollDown();
}

togglePlaintextPassword();
copyPasswordToPlaintextArea();

addQuestion();
displayNameOfSelectedFile();
togglePublishedInformationFormGroups();
toggleOtherOrganisationTextBox();

// ======== CALL PAGE SPECIFIC FUNCTIONS ========

if (window.location.pathname.includes('/dashboard/answer-questions/')) {
    setupQuillEditor();
}

if (window.location.pathname.includes('/user/how-can-i-help')) {
    highlightSelectedVolunteerOption();
    openVolunteerOptionDialog();
}
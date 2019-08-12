
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

function disableSubmitExcelButtonOnPageLoad() {
    $(document).ready(function() {
        $('.submit-excel').prop('disabled', true);
    });
}

function processSelectedExcelSheet() {
    $('#excelFileBrowser').change(function() {

        // remove browser inserted string from filename
        var file_name = $(this).val().replace('C:\\fakepath\\', '');

        // check if file has valid extension
        if (file_name.split('.').pop() == 'xlsx') {
            $('.excel-file-label i').removeClass('red');
            $('.excel-file-label i').addClass('green');
            $('.excel-file-label span').text(file_name);

            $('.validation-errors h5').html(
                '<i class="fas fa-cog fa-spin"></i> Checking for errors...'
            )
            $('.validation-errors h5').css('margin-bottom', '2rem');

            var form_data = new FormData();
            var excel_file = $('#excelFileBrowser')[0].files[0];
            form_data.append('excel_file', excel_file)

            // validate the excel file
            $.ajax({
                url: $(this).data('url'),
                type: 'POST',
                data: form_data,
                contentType: false,
                processData: false,
                success: function(response) {
                    if (response == 'validated') {
                        $('.validation-errors h5').html(
                            '<i class="far fa-check-circle green"></i> No errors found. Great job!'
                        )
                        $('.validation-errors h5').css('margin-bottom', '2rem');
                        $('.submit-excel').prop('disabled', false)
                    }
                    else {  
                        $('.validation-errors h5').html(
                            '<i class="far fa-times-circle red"></i> We found some errors in your excel file:'
                        )
                        $('.validation-errors .error-list').html(response)
                        $('.submit-excel').prop('disabled', true)
                    }
                },
                error: function(response) {
                    $('.validation-errors h5').html(
                        '<i class="far fa-times-circle red"></i> We are not able to read this file. Please get in touch with us to get help!'
                    )
                    $('.validation-errors h5').css('margin-bottom', '2rem');
                    $('.submit-excel').prop('disabled', true)
                }
            });
        }
        else {
            $('.excel-file-label i').removeClass('green');
            $('.excel-file-label i').addClass('red');
            $('.excel-file-label span').text("Invalid File Format! Click to select another file");
            $('.submit-excel').prop('disabled', true)
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

// ======== CALL PAGE SPECIFIC FUNCTIONS ========

if (window.location.pathname.includes('/dashboard/question/submit') || window.location.pathname.includes('/dashboard/manage-content')) {
    disableSubmitExcelButtonOnPageLoad();
    processSelectedExcelSheet();
}

if (window.location.pathname.includes('/dashboard/answer-questions/')) {
    setupQuillEditor();
}

if (window.location.pathname.includes('/user/how-can-i-help')) {
    highlightSelectedVolunteerOption();
    openVolunteerOptionDialog();
}
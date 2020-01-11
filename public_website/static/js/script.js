
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
            $('#mainLogo').css('width', '200px');
        }
        else {
            $('#mainLogo').css('width', '230px');
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

function setupNavbarSearchBar() {
    $('.navbar-search-icon').click(function() {
        $(this).toggleClass('active');
        $('.navbar-search-box').toggleClass('open');
    });

    $('.close-navbar-search-box').click(function(event) {
        event.preventDefault();
        $('.navbar-search-box').removeClass('open');
        $('.navbar-search-icon').toggleClass('active');
    });
}

function setupSearchResultsSearch() {
    $('.search-results-search').submit(function(event) {
        event.preventDefault();
        var current_params = new URLSearchParams(location.search);
        current_params.delete('q');
        current_params.append('q', $('.search-results-search-field').val());
        location.href = window.location.origin + window.location.pathname + '?' + current_params.toString();
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

function setupSearchResultsPagination() {
    $('.page-button').click(function() {
        var current_params = new URLSearchParams(location.search);
        current_params.set('page', $(this).data('page'));
        location.href = window.location.origin + window.location.pathname + '?' + current_params.toString();
    });
}

function setupSearchResultsSort() {
    $('.sort-by-option').click(function() {
        var current_params = new URLSearchParams(location.search);
        current_params.set('sort-by', $(this).data('sort'));
        location.href = window.location.origin + window.location.pathname + '?' + current_params.toString();
    });
}

function setupSearchResultsFilter() {
    $('.category-option').click(function() {
        if (!$(this).hasClass('.no-fun')) {
            var current_params = new URLSearchParams(location.search);
            if ($(this).hasClass('active')) {
                var new_params_list = []
                for (const value of current_params.entries()) {
                    if (value[1] == $(this).data('value')) {
                        if (value[0] != $(this).data('param')) {
                            new_params_list.push(value);
                        }
                    }
                    else {
                        new_params_list.push(value);
                    }
                }
                new_params = new URLSearchParams(new_params_list);

                if (new_params.toString() == '') {
                    location.href = window.location.origin + window.location.pathname + new_params.toString();
                }
                else {
                    location.href = window.location.origin + window.location.pathname + '?' + new_params.toString();
                }
            }
            else {
                current_params.delete('page');
                current_params.append($(this).data('param'), $(this).data('value'));
                location.href = window.location.origin + window.location.pathname + '?' + current_params.toString();
            }
        }
    });
}

function setupSearchResultsClearAll() {
    $('.clear-all').click(function() {
        var current_params = new URLSearchParams(location.search);
        var new_params_list = []

        for (const value of current_params.entries()) {
            if ((value[0] == 'page') || (value[0] == 'sort-by') || (value[0] == 'q')) {
                new_params_list.push(value);
            }
        }
        new_params = new URLSearchParams(new_params_list);

        if (new_params.toString() == '') {
            location.href = window.location.origin + window.location.pathname + new_params.toString();
        }
        else {
            location.href = window.location.origin + window.location.pathname + '?' + new_params.toString();
        }
    });
}

function setupQuillEditor({
        placeholder = null,
        inputName = 'rich-text-content'
    } = {}) {
    var quill = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: '#toolbar',
        },
        placeholder: placeholder,
    });

    $('.rich-text-form').submit(function(e) {
        var submitted_string = String(quill.root.innerHTML);
        var regex = new RegExp("<p><br></p>", "g");
        $('[name="' + inputName + '"]').val(submitted_string.replace(regex, ''));
    });
}

function activateTooltips() {
  $('[data-toggle="tooltip"]').tooltip()
}

/*
 * Comment delete buttons
 * These show the user a confirmation note before deciding whether to
 * actually delete the comment or not
*/

function setupCommentDeleteButtons() {
	$('.comment-delete-form')
    .attr('method', 'POST')
    .find('button.delete-button')
	.html('delete?')
	.click(function(e) {
	    e.preventDefault();
		$(this)
		.css('display', 'none')
		.next('span.delete-comment-prompt').show();
	});
	$('.comment-delete-form button.delete-cancel').click(function(e) {
		$(this)
		.parents('span.delete-comment-prompt').hide()
		.prev('button.delete-button').css('display', '')
		e.preventDefault();
	});
}

function setupCommentFormDisplayToggle() {
    $('.comment-form').hide();
    $('*[data-toggle="#comment-form"]')
    .click(function(e) {
        $('.comment-form').toggle();
    });
}

function setupDeleteReviewComment() {
    $('.delete-comment').click(function() {
        $(this).hide();
        $(this).next('.delete-comment-form').show();
    });

    $('.confirm-delete').click(function(event) {
        event.preventDefault();
        if ($(this).hasClass('delete-yes')) {
            $('.delete-comment-form').submit();
        }
        else {
            $('.delete-comment-form').hide();
            $('.delete-comment').show();
        }
    });
}

function setupBookmarkContentFunctionality() {
    $('.bookmark-button').click(function() {

        var form_data = new FormData();
        form_data.append('content', $(this).data('content'));
        form_data.append('id', $(this).data('id'));

        if ($(this).html() == '<i class="far fa-bookmark"></i> Bookmark') {

            // change the button icon and text
            $(this).html('<i class="fas fa-bookmark"></i> Bookmarked');
            $(this).addClass('bookmarked');

            // save bookmark
            $.ajax({
                url: location.origin + '/users/bookmark/add',
                type: 'POST',
                data: form_data,
                contentType: false,
                processData: false,
                success: function(response) {
                    console.log(response);
                },
                error: function(response) {
                    console.log(response);
                },
            });
        }
        else {
            $(this).html('<i class="far fa-bookmark"></i> Bookmark');
            $(this).removeClass('bookmarked');

            // remove bookmark
            $.ajax({
                url: location.origin + '/users/bookmark/remove',
                type: 'POST',
                data: form_data,
                contentType: false,
                processData: false,
                success: function(response) {
                    console.log(response);
                },
                error: function(response) {
                    console.log(response);
                },
            });
        }
    });
}

function enableLinkingtoTabs() {
    $(document).ready(function() {
        var hash = document.location.hash;
        if (hash) {
            $('.nav a[href="'+hash+'"]').tab('show');
        }

        $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
            window.location.hash = e.target.hash;
        });
    });
}

function setupViewNotification() {
    $('.notification-card').click(function() {
        $(this).children('.view-notification-form').submit();
    });
}

function setupHomePageCarouselRandomRhymes() {
    $('#homePageCarousel').on('slide.bs.carousel', function (event) {
        if (event.relatedTarget.classList.contains('rhyme-header')) {
            var rhymes_list = [
                'Leaves or fruits or sprouting shoots?',
                'Sun or stars or life on Mars?',
                'Constellations or the fate of nations?',
                'Curly tresses or yellow school buses?',
                'Birds in the sky or a firefly?'
            ]
            var current_rhyme = $('.first-banner-text').text();
            var available_rhymes_list = [];
            rhymes_list.forEach(function(element) {
                if (element != current_rhyme) {
                    available_rhymes_list.push(element);
                }
            });
            var next_rhyme = available_rhymes_list[Math.floor(Math.random() * available_rhymes_list.length)];
            $('.first-banner-text').text(next_rhyme);
        }
    });
}

// ======== CALL GENERAL FUNCTIONS ========

toggleNavbarMenu();
toggleUserMenu();
closeMenusOnClickingDarkbackground();
enableLinkingtoTabs();
setupNavbarSearchBar();
setupSearchResultsSearch();

// if (window.matchMedia("(min-width: 576px)").matches) {
//     resizeMainLogoOnScrollDown();
// }

// ======== CALL PAGE SPECIFIC FUNCTIONS ========

if (window.location.pathname == '/') {
    setupHomePageCarouselRandomRhymes();
}

if (window.location.pathname.includes('/dashboard/question/submit') || window.location.pathname.includes('/dashboard/manage-content')) {
    disableSubmitExcelButtonOnPageLoad();
    processSelectedExcelSheet();
}

if (new RegExp("^/dashboard/question/\\d+/answer/(new|\\d+)").test(window.location.pathname)) {
    setupQuillEditor({ placeholder: 'Type your answer here...' });
    activateTooltips();
}

if (new RegExp('^/dashboard/article/\\d+/edit').test(window.location.pathname)) {
    setupQuillEditor({});
    activateTooltips();
}

/* Breaking from tradition, this function is going intot the template so
 * that it can be better fine-tuned and generalised.

if (new RegExp('^/dashboard/article/\\d+/translate/from/[A-Za-z-]+/to/[A-Za-z-]+').test(window.location.pathname)) {
    setupQuillEditor({
        placeholder: 'Translation goes here...',
        inputName: 'body'
    })
}
*/


if (
    new RegExp("^/dashboard/article/\\d+/review").test(window.location.pathname) ||
    new RegExp("^/dashboard/question/\\d+/answers/\\d+/review").test(window.location.pathname)
) {
    // setupCommentFormDisplayToggle();
    // setupCommentDeleteButtons();
    setupDeleteReviewComment();
}

if (window.location.pathname.includes('/view-answer')) {
    setupDeleteReviewComment();
}

if (window.location.pathname.includes('/users/how-can-i-help')) {
    highlightSelectedVolunteerOption();
    openVolunteerOptionDialog();
}

if (
    window.location.pathname.includes('/dashboard/view-questions') ||
    window.location.pathname.includes('/dashboard/answer-questions') ||
    window.location.pathname.includes('/dashboard/review-answers') ||
    window.location.pathname.includes('/search')
   ) {
    setupSearchResultsPagination();
    setupSearchResultsSort();
    setupSearchResultsFilter();
    setupSearchResultsClearAll();
    setupBookmarkContentFunctionality();
}

if (window.location.pathname.includes('/user/')) {
    setupViewNotification();
}

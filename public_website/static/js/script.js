
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

function setupAccessSelection() {
    $('.access-item').click(function() {
        $(this).find('.selected-check').toggleClass('show');
        var access_form_field = $('input[name="' + $(this).data('permission') + '"]');
        if (access_form_field.val() == 'false') {
            access_form_field.val('true');
        }
        else {
            access_form_field.val('false');
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

function setupResultsPagination() {
    $('.page-button').click(function() {
        var current_params = new URLSearchParams(location.search);
        current_params.set('page', $(this).data('page'));
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

function setupUserListFilter() {
    $('.apply-user-filter').click(function() {
        var current_params = new URLSearchParams(location.search);
        current_params.delete('permission');
        current_params.delete('email');
        current_params.delete('page');
        $('input[name="user-permission"]:checked').each(function() {
            current_params.append('permission', $(this).val());
        });
        current_params.append('email', $('input[name="verified-email"]:checked').val());
        location.href = window.location.origin + window.location.pathname + '?' + current_params.toString();
    });
}

function setupSearchResultsMobileFilter() {
    // display mobile filter
    $('.mobile-filter-controls .filter-button').click(() => {
		if ($(this).data('show-filter')) {
			//$('.search-results').show()
			$('.filter-sidebar').hide()
			$(this).data('show-filter', false)
		} else {
			$('.filter-sidebar').show()
			$('.filter-sidebar').css('width', '100%')
			//$('.search-results').hide()
			$(this).data('show-filter', true)
		}
	})
}

function setupSearchResultsMobileSort() {
    // display mobile sort
    $('.mobile-filter-controls .sort-by-button').click(() => {
        if ($(this).data('show-menu')) {
            $('.mobile-sort-by-popup').hide()
            $(this).data('show-menu', false)
        } else {
            $('.mobile-sort-by-popup').show()
            $(this).data('show-menu', true)
        }
    })
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
    inputName = 'rich-text-content' } = {}) {

    Quill.register('modules/blotFormatter', QuillBlotFormatter.default);

    class SawaliramImageSpec extends QuillBlotFormatter.ImageSpec {
        getActions() {
            return [QuillBlotFormatter.DeleteAction, QuillBlotFormatter.ResizeAction];
        }
    }

    var quill = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: '#toolbar',
            blotFormatter: {
                specs: [
                    SawaliramImageSpec,
                ],
            },
        },
        placeholder: placeholder,
    });

    $('.rich-text-form').submit(function(e) {
        var submitted_string = String(quill.root.innerHTML);
        var regex = new RegExp("<p><br></p>", "g");
        var cleaned_submitted_string = submitted_string.replace(regex, '');
        if (cleaned_submitted_string != '') {
            $('[name="' + inputName + '"]').val(cleaned_submitted_string);
        } else {
            return false;
        }
    });
}

function setupSubmissionLanguageSelector() {
    $('.submission-language-select').change(function() {
        $('[name="submission-language"]').val($(this).val());
    });
}

function setupPublicationAutoFill() {
    $('.credit-title.added-later').change(function() {
        if ($(this).val() == 'publication') {
            $(this).next('.credit-user-name').val($(this).data('publication'));
        }
        else {
            if ($(this).next('.credit-user-name').val() == $(this).data('publication')) {
                $(this).next('.credit-user-name').val('');
            }
        }
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
            $(this).parent('.delete-comment-form').submit();
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

function setupAddCredit() {
    $('.add-credit').click(function(event) {
        event.preventDefault();
        var credit_form = $('.credits-card:first').clone().addClass('removable').appendTo('.credits-list'); 
        credit_form.find('.credit-user-name').val('').removeAttr('readonly').attr('value' ,'');
        credit_form.find('.credit-user-id').prop('value', '');
        credit_form.find('.credit-title').addClass('added-later');
        credit_form.find('.credit-title option[value="publication"]').css('display', 'block');
        setupRemoveCredit();
        setupPublicationAutoFill();
    });
}

function setupRemoveCredit() {
    $('.remove-credit-user').click(function(event) {
        event.preventDefault();
        $(this).parent('.credits-card').remove();
    });
}

setupAddCredit();
setupRemoveCredit();

function setupUserProfileMenuTabs() {

    if ($(window).width() < 768) {
        $('#userProfileMenuTabs .nav-link').on('show.bs.tab', function(event) {
            $('.user-profile-content').addClass('show');
        });
        $('#settingsTab').removeClass('active');
    }

    $('#userProfileMenuTabs .nav-link').click(function(event) {
        event.preventDefault();
        $(this).tab('show');
    });
}

function setupMobileCloseUserProfileContent() {

    $('.mobile-tab-content-controls button').click(function() {
        $('.tab-pane.active.show').removeClass('show');
        $('.user-profile-content').removeClass('show');
        $('.nav-link.active.show').removeClass('active');
    });
}

function setupChooseProfilePictureModal() {

    $('#changeProfilePictureModal').on('shown.bs.modal', function(event) {
        $.ajax({
            url: location.origin + '/get-profile-pictures-form',
            type: 'GET',
            success: function(response) {
                $('#changeProfilePictureModal .choose-picture-form-container').html(response);
            },
            error: function(response) {
                console.log(response);
            },
        });
    });
}

function setupToggleCardDrawer() {

    $('.open-card-drawer').click(function() {
        $(this).parent('.card-controls').next('.card-drawer').css('display', 'flex');
        $(this).hide();
    });

    $('.close-card-drawer').click(function() {
        $(this).parent('.card-drawer').css('display', 'none');
        $(this).parents('.card').find('.open-card-drawer').show();
    });
}

function setupGeneralContentSort() {
    $('.sort-by-option').click(function() {
        var current_params = new URLSearchParams(location.search);
        current_params.set('sort-by', $(this).data('sort'));
        location.href = window.location.origin + window.location.pathname + '?' + current_params.toString();
    });
}

function setupEditorToolbarSticky() {
    const navbarHeight = $('.navbar').outerHeight();
    const ckEditorElement = $('.editor-container .ck.ck-reset.ck-editor.ck-rounded-corners');
    const stickyPanelElement = $('.editor-container .ck.ck-reset.ck-editor.ck-rounded-corners .ck.ck-sticky-panel');
    const toolbarElement = stickyPanelElement.find('.ck.ck-toolbar.ck-toolbar_grouping');

    window.onscroll = function() {
        if (window.pageYOffset > ckEditorElement.offset().top - navbarHeight) {
            stickyPanelElement.css('position', 'fixed');
            stickyPanelElement.css('top', navbarHeight + 'px');
            stickyPanelElement.css('width', ckEditorElement.width() + 'px');
            stickyPanelElement.css('z-index', '1000');
            toolbarElement.css('border-radius', '0');
            toolbarElement.css('border-bottom', '1px solid #c4c4c4');
        }
        else {
            stickyPanelElement.css('position', '');
            stickyPanelElement.css('top', '');
            stickyPanelElement.css('width', '');
            stickyPanelElement.css('z-index', '');
            toolbarElement.css('border-radius', '');
            toolbarElement.css('border-bottom', '');
        }
    };
}

function initializeCKEditor() {
    ClassicEditor
        .create(document.querySelector( '#editor' ), {
            toolbar: {
                items: ['heading', '|', 'bold', 'italic', 'underline', '|', 'bulletedlist', 'numberedlist', 'indent', 'outdent', 'blockquote', 'horizontalline', '|', 'specialcharacters', 'mathtype', 'chemtype', 'subscript', 'superscript', '|', 'link', 'imageupload', 'inserttable', '|', 'undo', 'redo'],
                viewportTopOffset: $('.navbar').outerHeight(),
            },    
            placeholder: 'Type your article here...',
            image: {
                toolbar: ['imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight'],
                styles: ['full', 'alignLeft', 'alignRight']
            },
            table: {
                contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells']
            },
            link: {
                addTargetToExternalLinks: true
            }
        })
        .then(editor => {
            const wordCountPlugin = editor.plugins.get( 'WordCount' );
            const wordCountWrapper = $('#wordCountWrapper');
            wordCountWrapper.append(wordCountPlugin.wordCountContainer);
            setupEditorToolbarSticky();
        })
        .catch(error => {
            console.error( error );
        });
}

function setupEditorLanguageSelector() {
    $('.language-option').click(function() {
        $('[name="language"]').val($(this).data('code'));
        $('.selected-language').text($(this).text());
    });
}

function setupCreditTitleSelector() {
    $('.credit-title-option').click(function() {
        $(this).parents('.dropdown').find('.selected-title').text($(this).text());
        $(this).parents('.credit-entry').find('[name="credit-title"]').val($(this).data('title'));
    });
}

function setupAddCreditEntry() {
    $('.add-credit-entry').click(function() {
        var credit_entry = $('.credit-entry:first').clone().addClass('removable').appendTo('.credit-entry-list');
        credit_entry.find('.credit-user-name').val('').removeAttr('readonly').attr('value' ,'');
        credit_entry.find('.credit-user-id').prop('value', '');
        credit_entry.find('.credit-title').prop('value', 'author');
        setupCreditTitleSelector();
        setupRemoveCreditEntry();
    });
}

function setupRemoveCreditEntry() {
    $('.remove-credit-entry').click(function() {
        $(this).parent('.credit-entry').remove();
    });
}

function setupEditorDeleteFunctionality() {
    $('button.editor-delete').click(function() {
        $('.submit-container').hide();
        $('.delete-container').show();
    });

    $('.editor-cancel-delete').click(function() {
        $('.delete-container').hide();
        $('.submit-container').show();
    });
}

setupToggleCardDrawer();
setupChooseProfilePictureModal();
setupMobileCloseUserProfileContent();
setupUserProfileMenuTabs();

function autoResizeSelectFields() {

    /* * * * * * * * * * * * * * * * * * * * * * * * * * * *
     * Solution thanks to João Pimentel Ferreira           *
     * in the following  StackOverflow answer:             *
     *                                                     *
     *     https://stackoverflow.com/a/55343177/1196444    *
     *                                                     *
     * * * * * * * * * * * * * * * * * * * * * * * * * * * */

    $('select').change(function(){
        var text = $(this).find('option:selected').text()
        var $aux = $('<select/>').append($('<option/>').text(text))
        $(this).after($aux)
        $(this).width($aux.width())
        $aux.remove()
    }).change()
}

function setupRemoveCreditEntry() {
    $('.remove-credit-entry').click(function() {
        $(this).parent('.credit-entry').remove();
    });
}

function setupEditorDeleteFunctionality() {
    $('button.editor-delete').click(function() {
        $('.submit-container').hide();
        $('.delete-container').show();
    });

    $('.editor-cancel-delete').click(function() {
        $('.delete-container').hide();
        $('.submit-container').show();
    });
}

setupToggleCardDrawer();
setupChooseProfilePictureModal();
setupMobileCloseUserProfileContent();
setupUserProfileMenuTabs();

// ======== CALL GENERAL FUNCTIONS ========

toggleNavbarMenu();
toggleUserMenu();
closeMenusOnClickingDarkbackground();
enableLinkingtoTabs();
setupNavbarSearchBar();
setupSearchResultsSearch();
setupGeneralContentSort();
autoResizeSelectFields();

// ======== CALL PAGE SPECIFIC FUNCTIONS ========

if (window.location.pathname == '/') {
    setupHomePageCarouselRandomRhymes();
}

if (window.location.pathname.includes('/dashboard/question/submit') || window.location.pathname.includes('/dashboard/manage-content')) {
    disableSubmitExcelButtonOnPageLoad();
    processSelectedExcelSheet();
}

if (window.location.pathname.includes('/dashboard/manage-users')) {
    setupUserListFilter();
    setupResultsPagination();
}

if (
    new RegExp("^/dashboard/translate/(articles|answers|questions)/(\\d+/)?\\d+/(review|edit)").test(window.location.pathname) ||
    new RegExp("^/dashboard/question/\\d+/answer/(new|\\d+)").test(window.location.pathname)
) {
    initializeCKEditor();
    setupEditorLanguageSelector();
    setupCreditTitleSelector();
    setupAddCreditEntry();
    setupRemoveCreditEntry();
    setupEditorDeleteFunctionality();
}

if (new RegExp('^/dashboard/article/\\d+/edit').test(window.location.pathname)) {
    initializeCKEditor();
    setupEditorLanguageSelector();
    setupCreditTitleSelector();
    setupAddCreditEntry();
    setupRemoveCreditEntry();
    setupEditorDeleteFunctionality();
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
    new RegExp("^/dashboard/question/\\d+/answers/\\d+/review").test(window.location.pathname) ||
    new RegExp("^/dashboard/translate/articles/\\d+/review").test(window.location.pathname) ||
    new RegExp("^/dashboard/translate/answers/\\d+/review").test(window.location.pathname)
) {
    setupDeleteReviewComment();
}

if (window.location.pathname.includes('/view-answer')) {
    setupDeleteReviewComment();
}

if (window.location.pathname.includes('/users/request-access')) {
    setupAccessSelection();
}

if (
    window.location.pathname.includes('/dashboard/view-questions') ||
    window.location.pathname.includes('/dashboard/answer-questions') ||
    window.location.pathname.includes('/dashboard/review-answers') || 
    window.location.pathname.includes('/dashboard/translate/answers') || 
    window.location.pathname.includes('/search')
   ) {
    setupResultsPagination();
    setupSearchResultsFilter();
    setupSearchResultsMobileFilter();
    setupSearchResultsMobileSort();
    setupSearchResultsClearAll();
    setupBookmarkContentFunctionality();
}

if (window.location.pathname.includes('/user/')) {
    setupViewNotification();
}

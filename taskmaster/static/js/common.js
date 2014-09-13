var TEMPLATES = {};
var COOKIES = {
  view: 'view',
  org: 'org'
};

$(function() {
  // Load Templates
  _.each($('[type="underscore"]'), function(ele) {
    var $ele = $(ele);
    TEMPLATES[$ele.data('template-name')] = _.template($ele.html());
  });

  $('#org-selector').html(TEMPLATES['org-selector'](STATE.orgs, STATE.org, STATE.users, STATE.user));

  $('.left-nav > li > a').click(function() {
    var activeContent = $('.left-nav > li.active > a').attr('href');
    //Whatever is currently showing, hide it
    activeTab = $('.left-nav > li.active');
    activeTab.removeClass('active');

    //Add active to nav
    $(this).parents('li').addClass('active');
    //hide content
    $(activeContent).removeClass('active');
    $(activeContent).addClass('hidden');
    // show content
    var targetContent = $(this).attr('href');
    $(targetContent).removeClass('hidden');
    $(targetContent).addClass('active');
  });

  $('body').on('click', '#logout', function(e) {
    e.preventDefault();
    e.stopPropagation();

    $.ajax({
      url: '/logout',
      type: 'POST'
    });

    window.location = "/signup";
  });

  $('body').on('click', '#project-admin', function(e) {
    org = $('#org-dropdown').val();
    if(org) {
      $.cookie(COOKIES.org, org);
      window.location = "/project-admin";
    }
  });

  $('body').on('click', '#project-tasks', function(e) {
    org = $('#org-dropdown').val();
    if(org) {
      $.cookie(COOKIES.org, org);
      window.location = "/";
    }
  });

  $('body').on('change', '#org-dropdown', function(e) {
    org = $(this).val();
    $.cookie(COOKIES.org, org);

    if($('#project-admin').hasClass('selected')) {
      window.location = "/project-admin";
    } else {
      window.location = "/";
    }
  });

  $('a[href="' + window.location.hash + '"]').click();
});

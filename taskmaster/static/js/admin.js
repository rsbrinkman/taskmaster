  
  var TEMPLATES = {}
  $('.name').blur(function() {
    var $this = $(this);
    var name = $this.html();

    $.ajax({
      type: 'PUT',
      url: '/user/' + $.cookie('user') +'/name',
      data: {
        name: name
      },
      success: function() {
        $('.updates').append('Updated!');  
      }
    });
  });
  $('.container').on('click', '.join-org', function() {
    email = $('.username').text();
    orgname = $(this).data('org-name');
    addUserToOrg(email, orgname);
  });
  function addUserToOrg(email, orgname) {
    $.ajax({
      type: 'POST',
      url: '/org/' + orgname + '/user/' + email,
      success: function(org) {
        $('.user-org-results').empty()
        $('.user-org-results').append(email + ' added to ' + org.name + ' successfully!');
        $('.no-org').empty()
        $('.my-org-list').append('<li data-org-id="' + org.id + '">' + org.name + '</li>');
        $('.org-list').append('<option name="' + org.name + '" + value="' + org.id + '" >' + org.name + '</option>');
        $('.task-home').removeAttr('disabled');
      }
    });
  };
  
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

  function loadTemplates() {
    _.each($('[type="underscore"]'), function(ele) {
      var $ele = $(ele);
      TEMPLATES[$ele.data('template-name')] = _.template($ele.html());
    });
  }
  loadTemplates();
  $('#org-selector').html(TEMPLATES['org-selector'](STATE.orgs, STATE.org, STATE.users, STATE.user));
  $('#settings').html(TEMPLATES['settings'](STATE.orgs, STATE.org, STATE.users, STATE.user));
  $('#invite').html(TEMPLATES['invite']());
  $('#search').html(TEMPLATES['search']());
  $('#projects').html(TEMPLATES['projects'](STATE.orgs));

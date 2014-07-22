$(function() {
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

  $('#settings').html(TEMPLATES['settings'](STATE.orgs, STATE.org, STATE.users, STATE.user));
  $('#invite').html(TEMPLATES['invite']());
  $('#search').html(TEMPLATES['search']());
  $('#projects').html(TEMPLATES['projects'](STATE.orgs));

  $('.user-button').addClass('selected');
});

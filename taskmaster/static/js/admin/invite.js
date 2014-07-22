$(function() {
  $('#add-user').click(function () {
    var email = $('#user').val();
    var orgname = $('#org').val();
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
});

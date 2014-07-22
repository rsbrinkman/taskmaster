$(function() {
  $('#add-user').click(function () {
    var email = $('#user').val();
    var orgname = $('#org').val();
    addUserToOrg(email, orgname);
  });
});

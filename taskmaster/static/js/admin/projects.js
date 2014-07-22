$(function() {
  $('#create-org').click(function () {
    var org = $('#org-name').val();
    $.ajax({
      type: 'POST',
      url: '/org/',
      data: {'name': org},
      success: function(org) {
        $('.org-creation-results').empty()
        $('.org-creation-results').append(org.name + ' created!');
        $('.my-org-list').append('<li data-org-id="' + org.id + '">' + org.name + '</li>');
        // Check to make sure there is an org cookie to prevent weird edge case.
        var selectedOrg = $.cookie('org')
        if (!selectedOrg) {
          $.cookie('org', org.id);
        }
      }
    });
  });

  $('.task-home').click(function () {
    selectedOrg = $('.org-dropdown').val();
    console.log('selectedOrg');
    $.cookie('org', selectedOrg);
    window.location.href = '/';
  });
});

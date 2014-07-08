  $('#create-org').click(function () {
    var org = $('#org-name').val();
    $.ajax({
      type: 'POST',
      url: '/org/' + org,
      success: function(org) {
        $('.org-creation-results').empty()
        $('.org-creation-results').append(org.name + ' created!');
        $('.my-org-list').append('<li data-org-id="' + org.id + '">' + org.name + '</li>');
      }
    });
  });



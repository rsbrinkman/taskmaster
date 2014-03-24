  $('#create-org').click(function () {
    var org = $('#org-name').val();
    var users = $('#users').val();
    console.log(org);
    console.log(users);
    $.ajax({
      type: 'POST',
      url: '/org/' + org,
      data:{ 'users': users },
    });
  });
  $('#create-user').click(function () {
    var email = $('#email').val();
    var name = $('#name').val();
    $.ajax({
      type: 'POST',
      url: '/user',
      data:{ 
        'email': email, 
        'name': name
      },
      success: function() {
        window.location = "/admin?user=" + email;
        }
    });
  });
  $('#add-user').click(function () {
    var email = $('#user').val();
    var org = $('#org').val();
    $.ajax({
      type: 'POST',
      url: '/org/' + org + '/user/' + email,
    });
  });
  $('#search').click(function () {
    var org = $('#org-search').val();
    $.ajax({
      type: 'POST',
      url: '/orgs/' + org,
      success: function(data) {
        // display the results
        if (!data) {
            $('.search-results').append('No Search results found');
        }
        else {
          $.map(data, function(k, v) {
            $('.search-results').append(v);
          });
        }

      }
    });
  });

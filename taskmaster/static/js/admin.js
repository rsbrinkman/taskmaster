  $('#create-org').click(function () {
    var org = $('#org-name').val();
    var users = $('#users').val();
    $.ajax({
      type: 'POST',
      url: '/org/' + org,
      data:{ 'users': users },
      success: function() {
        $('.org-creation-results').append(org + ' created!');
      }
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
      success: function() {
        $('.user-org-results').empty()
        $('.user-org-results').append(email + ' added to ' + org + ' successfully!');
        $('.my-org-list').append('<li>' + org + '</li>');
      }
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
            $('.search-results').empty()
            $('.search-results').append('No Search results found');
        }
        else {
            $('.search-results').append(data);
        }

      }
    });
  });

  $('#create-org').click(function () {
    var org = $('#org-name').val();
    var users = $('#users').val();
    $.ajax({
      type: 'POST',
      url: '/org/' + org,
      data:{ 'users': users },
      success: function() {
        $('.org-creation-results').empty()
        $('.org-creation-results').append(org + ' created!');
        $('.my-org-list').append('<li>' + org + '</li>');
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
        $.cookie('user', email);
        }
    });
  });
  $('#add-user').click(function () {
    var email = $('#user').val();
    var org = $('#org').val();
    addUserToOrg(email, org);
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
            $('.search-results').empty()
            $('.search-results').append(data + "<button data-org=" + data + " class='btn btn-sm join-org'>Join</button>");
        }

      }
    });
  });
  $('.task-home').click(function () {
    selectedOrg = $('.org-list').val();
    $.cookie('org', selectedOrg);
    window.location.href = '/';
  });
  $('.container').on('click', '.join-org', function() {
    email = $.cookie('user');
    org = $(this).data('org');
    addUserToOrg(email, org);
  });
  function addUserToOrg(email, org) {
    $.ajax({
      type: 'POST',
      url: '/org/' + org + '/user/' + email,
      success: function() {
        $('.user-org-results').empty()
        $('.user-org-results').append(email + ' added to ' + org + ' successfully!');
        $('.no-org').empty()
        $('.my-org-list').append('<li>' + org + '</li>');
        $('.org-list').append('<option name=' + org + '>' + org + '</option>');
        $('.task-home').removeAttr('disabled');
      }
    });
  };


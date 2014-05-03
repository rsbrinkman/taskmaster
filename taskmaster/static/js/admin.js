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

  $('#sign-up-form').submit(function (e) {
    e.preventDefault();

    var $this = $(this),
        email = $this.find('input[name=email]').val(),
        name = $this.find('input[name=name]').val(),
        password = $this.find('input[name=password]').val(),
        passwordConfirm = $this.find('input[name=password-confirm]').val(),
        $error = $this.find('.error'),
        errorMessage = '';


    if (passwordConfirm !== password) {
      errorMessage = "Passwords do not match";
    }

    $error.text(errorMessage);

    if (!errorMessage) {
      $.ajax({
        type: 'POST',
        url: '/user',
        data:{
          'email': email,
          'name': name,
          'password': password
        },
        success: function(token) {
          $.cookie('user', email);
          $.cookie('token', token);
          window.location = "/admin";
        },
        error: function(jqXHR, textStatus, errorThrown) {
          $error.text(jqXHR.responseText);
        }
      });
    }
  });

  $('#login-form').submit(function (e) {
    e.preventDefault();

    var $this = $(this),
        email = $this.find('input[name=email]').val(),
        password = $this.find('input[name=password]').val(),
        $error = $this.find('.error');

    $.ajax({
      type: 'POST',
      url: '/authenticate',
      data:{
        'email': email,
        'password': password
      },
      success: function(token) {
        $.cookie('token', token);
        $.cookie('user', email);
        window.location = "/";
      },
      error: function(jqXHR, textStatus, errorThrown) {
        $error.text(jqXHR.responseText);
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


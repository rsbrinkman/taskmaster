  $('#create-org').click(function () {
    $.ajax({
      type: 'POST',
      url: '/org/',
      data: {
        name: $('#org-name').val()
      },
      success: function(org) {
        $('.org-creation-results').empty()
        $('.org-creation-results').append(org.name + ' created!');
        $('.my-org-list').append('<li data-org-id="' + org.id + '">' + org.name + '</li>');
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
        url: '/user/',
        data:{
          'email': email,
          'name': name,
          'password': password
        },
        success: function(user) {
          $.cookie('user', user.id);
          $.cookie('token', user.token);
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
      success: function(user) {
        $.cookie('token', user.token);
        $.cookie('user', user.id);
        window.location = "/";
      },
      error: function(jqXHR, textStatus, errorThrown) {
        $error.text(jqXHR.responseText);
      }
    });
  });

  $('#add-user').click(function () {
    var email = $('#user').val();
    var orgname = $('#org').val();
    addUserToOrg(email, orgname);
  });

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
  $('#search').click(function () {
    $.ajax({
      type: 'GET',
      url: '/search/orgs/',
      data: {
        term: $('#org-search').val()
      },
      success: function(data) {
        // display the results
        if (!data) {
            $('.search-results').empty()
            $('.search-results').append('No Search results found');
        }
        else {
            $('.search-results').empty()
            $('.search-results').append(data.name + '<button data-org-id="' + data.id + '" data-org-name="' + data.name + '" class="btn btn-sm join-org">Join</button>');
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


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



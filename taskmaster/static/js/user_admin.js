require.config({
  paths: {
    "templates": "../templates",
    "jquery": "/static/js/jquery-2.0.3.min",
    "underscore": "/static/js/underscore-min",
    "backbone": "/static/js/backbone-1.1.2.min",
    "jquery-cookie": "/static/js/jquery.cookie",
    "jquery-ui": "/static/js/jquery-ui-1.10.4.custom.min"
  },

  shim: {
      backbone: {
          deps: ["underscore", "jquery"],
          exports: "Backbone"
      },

      underscore: {
          exports: "_"
      },

      'jquery-ui': {
          deps: ['jquery']
      },

      'jquery-cookie': {
          deps: ['jquery']
      }
  }

});

require([
    'views/user_projects',
    'views/find_projects',
    'views/user_settings',
    'app_state',
    'jquery-cookie'
], function(UserProjectsView, FindProjectsView, UserSettingsView, AppState) {
  var appState = new AppState();
  appState.populate();

  $(function() {
    var userProjects = new UserProjectsView({
      el: '#projects',
      appState: appState
    }).render();

    var findProjects = new FindProjectsView({
      el: '#search',
      appState: appState
    }).render();

    var userSettings = new UserSettingsView({
      el: '#settings',
      appState: appState
    }).render();

    $('.user-button').addClass('selected');
  });
});

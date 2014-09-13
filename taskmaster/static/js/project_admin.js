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
    'views/project_users',
    'views/project_settings',
    'app_state',
    'jquery-cookie'
], function(ProjectUsersView, ProjectSettingsView, AppState) {
  var appState = new AppState();
  appState.populate();

  $(function() {
    var projectUsers = new ProjectUsersView({
      el: '#users',
      appState: appState
    }).render();


    var projectSettings = new ProjectSettingsView({
      el: '#settings',
      appState: appState
    }).render();

    $("#project-admin").addClass('selected');
  });
});

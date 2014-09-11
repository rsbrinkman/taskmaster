require.config({
  paths: {
    "templates": "../templates",
    "jquery": "/static/js/jquery-2.0.3.min",
    "underscore": "/static/js/underscore-min",
    "backbone": "/static/js/backbone-1.1.2.min"
  },

  shim: {
      backbone: {
          deps: ["underscore", "jquery"],
          exports: "Backbone"
      },

      underscore: {
          exports: "_"
      }
  }

});

require(['views/project_users', 'app_state'], function(ProjectUsersView, AppState) {
  var appState = new AppState();
  appState.populate();

  $(function() {
    _.each(['settings'], function(id) {
      $('#' + id).html(TEMPLATES[id]({STATE: STATE}));
    });

    var projectUsers = new ProjectUsersView({
      el: '#users',
      appState: appState
    }).render();

    $("#project-admin").addClass('selected');
  });
});

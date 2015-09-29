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

require(['admin/project_users'], function(ProjectUsersView) {
  $(function() {
    _.each(['settings'], function(id) {
      $('#' + id).html(TEMPLATES[id]({STATE: STATE}));
    });

    var projectUsers = new ProjectUsersView({
      el: '#users'
    }).render();

    $("#project-admin").addClass('selected');
  });
});

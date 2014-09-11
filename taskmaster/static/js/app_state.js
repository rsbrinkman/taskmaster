define([
  'models/project_users',
  'models/user',
  'models/project'
], function(ProjectUsers, User, Project) {

  // TODO eventually should grab this data piecemeal from
  // the server instead of rendering everything
  var AppState = function() {

  };

  AppState.prototype.populate = function () {
    this.currentUser = new User();
    this.currentUser.fetch();

    this.currentProject = new Project();
    this.currentProject.fetch();

    this.currentProjectUsers = new ProjectUsers();
    this.currentProjectUsers.fetch();
  };

  return AppState;
});

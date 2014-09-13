define([
  'models/project_users',
  'models/user',
  'models/project',
  'models/common'
], function(ProjectUsers, User, Project, Common) {

  var AppState = function() {

  };

  AppState.prototype.populate = function () {
    this.currentUser = new User();
    this.currentUser.fetch();

    this.currentProject = new Project();
    this.currentProject.fetch();

    this.currentProjectUsers = new ProjectUsers();
    this.currentProjectUsers.fetch();

    this.common = new Common();
    this.common.fetch();
  };

  return AppState;
});

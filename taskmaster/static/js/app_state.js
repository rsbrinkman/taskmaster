define([
  'models/current_project_users',
  'models/current_user',
  'models/current_project'
], function(CurrentProjectUsers, CurrentUser, CurrentProject) {

  // TODO eventually should grab this data piecemeal from
  // the server instead of rendering everything
  var AppState = function() {

  };

  AppState.prototype.populate = function () {
    this.currentUser = new CurrentUser();
    this.currentUser.fetch();

    this.currentProject = new CurrentProject();
    this.currentProject.fetch();

    this.currentProjectUsers = new CurrentProjectUsers();
    this.currentProjectUsers.fetch();
  };

  return AppState;
});

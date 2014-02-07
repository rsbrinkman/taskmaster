var FilterTasks = (function() {
  var nonWordChars = new RegExp(/[^\w']+/);
  var taskTokens = {};
  var fieldsToFilterOn = ['name', 'tags'];

  function buildTokenSets(tasks) {
    _.each(tasks, function(task) {
      
      // Collect tokens
      var tokens = [];
      _.each(fieldsToFilterOn, function(field) {
        tokens = tokens.concat(task[field].split(nonWordChars));
      });

      // Store tokens as a set for quick membership testing
      // Include all prefixes of the token for partial matches,
      // i.e. "hel" matches "hello"
      var tokenSet = {}
      _.each(tokens, function(token) {
        token = token.toLowerCase();
        for(var l = 1; l <= token.length; l++) {
          tokenSet[token.slice(0, l)] = true;
        }
      });
      taskTokens[task.id] = tokenSet;
    });
  }

  function isAccepted(taskId, searchTokens) {
    if (!taskTokens[taskId]) {
      return false;
    }

    return _.every(searchTokens, function(token) {
      return token in taskTokens[taskId];
    });
  }

  return {
    buildTokenSets: buildTokenSets,
    isAccepted: isAccepted
  };

})();

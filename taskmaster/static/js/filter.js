
var FilterTasks = (function() {
  var whitespace = new RegExp(/\s+/);
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

  function matchSearchTokens(task, searchTokens) {
    if (!taskTokens[task.id]) {
      return false;
    }

    return _.every(searchTokens, function(token) {
      return token in taskTokens[task.id];
    });
  }

  CompiledFilter = (function() {
    function CompiledFilter(rule) {
      var that = this;
      this.matchTests = [];
      var searchTokens = [];

      if (!rule) {
        this.matchTests.push(function(task) {
          return true;
        });
        return
      }

      _.each(rule.trim().toLowerCase().split(whitespace), function(t) {
        var colonOperator = t.indexOf(':');

        if (colonOperator < 0) {
          // Just a normal text search
          searchTokens.push(t);
        } else {
          var key = t.substr(0, colonOperator);
          var value = t.substr(colonOperator + 1);

          // TODO validate 'key' for now assume it is an attribute on
          // task that can be compared to the value directly
          var matchTest = function(task) {
            return _.some(value.split(','), function(v) {
              v = v.trim().toLowerCase();
              if (!v.length) {
                return true;
              }

              if (v[0] === '!') {
                return task[key] !== v;
              } else {
                return task[key] === v;
              }
            });
          };

          that.matchTests.push(matchTest);
        }
      });

      this.matchTests.push(function(task) {
        return matchSearchTokens(task, searchTokens);
      });

    }

    CompiledFilter.prototype.match = function(task) {
      return _.every(this.matchTests, function(test) {
        return test(task);
      });
    };

    return CompiledFilter;
  })();

  function compileFilter(rule) {
    return new CompiledFilter(rule);
  }

  return {
    buildTokenSets: buildTokenSets,
    compileFilter: compileFilter
  };

})();

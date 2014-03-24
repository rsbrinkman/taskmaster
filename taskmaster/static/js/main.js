var TEMPLATES = {}
var styleRules;
var COOKIES = {
  view: 'view'
}

$(function() {
  loadTemplates()

  // Used for quick filtering, need to call everytime we add/remove tokens to a task
  FilterTasks.buildTokenSets(STATE.taskmap);

  // Initialize these so the underscore template doesn't complain
  _.each(STATE.queuemap, function(queue) {
    queue.selected = false;
  });
  _.each(STATE.filtermap, function(filter) {
    filter.selected = false;
  });

  compileFilters();

  styleRules =_.map(STATE.preferences.style_rules, function(styleRule) {
    return {
      filter: FilterTasks.compileFilter(styleRule.rule),
      cssClass: styleRule.class
    }
  });

  loadCookies();
  renderView();
  setEventHandlers();
});

function compileFilters() {
  _.each(STATE.filtermap, function(filter) {
    if (!filter.compiled) {
      filter.compiled = FilterTasks.compileFilter(filter.rule);
    }
  });
}

function loadTemplates() {
  _.each($('[type="underscore"]'), function(ele) {
    var $ele = $(ele);
    TEMPLATES[$ele.data('template-name')] = _.template($ele.html());
  });
}

function setEventHandlers() {
  $('#task-view').on('click', '.del-task', function() {
    var $cell = $(this);
    var id = $cell.data('task-id');
    $.ajax({
      url: '/task/' + id,
      type: 'DELETE',
      success: function() {
        removeTask(id);
      }
    });
  });

  $('.container').on('click', '.delete-queue', function() {
    var $this = $(this);
    var id = $(this).data('queue-id');
    $.ajax({
      url: '/queue/' + id,
      type: 'DELETE',
      success: function() {
        removeQueue(id);
      }
    });
  });

  $('.container').on('click', '.queue-row', function(e) {
    if(e.target === this) {
      var $this = $(this);
      var id = $this.find('a').data('queue-id');
      STATE.queuemap[id].selected = !STATE.queuemap[id].selected;
      renderView();
    }
  });
  
  $('.container').on('change', '.task-queues', function(e) {
    var queue = $(this).val();
    var taskId = $(this).data('task-id');
    putTaskInQueue(taskId, queue);
  });
  
  $('#org-dropdown').change(function() {
    org = $(this).val();
    console.log(org);
    STATE.org = org
    $.ajax({
      url: '/',
      type: 'GET',
      data: {
        org: org
      }
    });

    console.log(STATE.org);
    renderView();
  });
  
  $('.container').on('change', '.task-assignee', function(e) {
    var assignee = $(this).val();
    var taskId = $(this).data('task-id');
    $.ajax({
      url: '/task/' + taskId  + '/update/' + 'assignee/' + assignee,
      type: 'POST',
      success: function() {
        STATE.taskmap[taskId].assignee = assignee;
      }
    });
  });

  $('.container').on('change', '.task-description', function() {
     var taskId = $('.description-container').data('task-id');
     var description = $('.task-description').val();
     $.ajax({
      url: '/task/' + taskId  + '/update/' + 'description/' + description,
      type: 'POST',
      success: function() {
        STATE.taskmap[taskId].description = description;
      }
    });
 
  });
  $('#create-queue').click(function(){
    createQueue($('#queue-name').val());
  });

  $('#queue-name').keyup(function(ev) {
    if (ev.which === 13) {
      createQueue($('#queue-name').val());
    }
  });

  $('.container').on('change', '.task-status', function() {
    var status = $(this).val();
    var taskId = $(this).data('task-id');
    $.ajax({
      url: '/task/' + taskId  + '/update/' + 'status/' + status,
      type: 'POST'
    });

    STATE.taskmap[taskId].status = status;
    renderView();
  });

  $('body').on('click', '.create-tasks', function() {
    $('.create-form-container').toggleClass('hidden');
    STATE.showingCreateTask = !STATE.showingCreateTask;
  });

  $('#filter-tasks-go').click(function() {
    STATE.searchString = $('#filter-tasks').val();
    renderView();
  });

  $('#filter-tasks').keyup(function(ev) {
    if (ev.which === 13) {
      STATE.searchString = $('#filter-tasks').val();
      renderView();
    }
  });

  $('#queue-list').sortable({
    stop: function(e, ui) {
      var queues = $(this).sortable('toArray', {attribute: 'data-queue-id'});
      reorderList(queues, STATE.queues, '/order/queue/');
      STATE.queues = queues;
    }
  });

  $('#save-filter').click(function() {
    saveFilter();
  });

  $('#save-filter-name').keyup(function(ev) {
    if (ev.which === 13) {
      saveFilter();
    }
  });

  $('#saved-filters').on('click', '.remove-filter', function(ev) {
    var name = $(this).data('name');
    $.ajax({
      url: '/filter/' + name + '/',
      type: 'DELETE'
    });

    delete STATE.filtermap[name];
    renderView();
  });

  $('#saved-filters').on('change', 'input[type="checkbox"]', function(ev) {
    var $this = $(this);

    var selected = $this.prop('checked');
    var name = $this.data('name');

    STATE.filtermap[name].selected = selected;
    renderView();
  });
}

function saveFilter() {
  var name = $('#save-filter-name').val();
  var rule = $('#filter-tasks').val();

  if (name && rule) {
    $.ajax({
      url: '/filter/' + name + '/',
      type: 'POST',
      data: {
        rule: rule
      }
    });

    STATE.filtermap[name] = {
      name: name,
      rule: rule,
      selected: true
    }

    $('#save-filter-name, #filter-tasks').val('');
    compileFilters();
    renderView();
  }
}

function reorderList(sortedList, prevList, url) {
  // Check if the order has changed
  if(JSON.stringify(sortedList) !== JSON.stringify(prevList)) {
    // Generate a list of [new_position1, queue1, new_position2, queue2, ...]
    var updates = [];
    _.each(prevList, function(itemName, index) {
      if (itemName !== sortedList[index]) {
        updates.push(sortedList.indexOf(itemName));
        updates.push(itemName);
      }
    });

    $.ajax({
      type: 'PUT',
      url: url,
      data: {
        updates: JSON.stringify(updates)
      }
    });
  }
}

function createQueue(queue) {
  $.ajax({
    url: '/queue/' + queue,
    type: 'POST',
    success: function(queue) {
      addQueue(queue);
      renderView();

      // Wipe the input field to make it more clear it was processed
      $('#queue-name').val('');
    }
  });
}

function removeTask(id) {
  delete STATE.taskmap[id];
  removeEle(STATE.tasks, id);
  _.each(STATE.queuemap, function(queue) {
    removeEle(queue.tasks, id);
  });
  renderView();
}

function addTask(task) {
  STATE.tasks.push(task.id);
  STATE.taskmap[task.id] = task;
  if (task.queue) {
    putTaskInQueue(task.id, task.queue);
  }
  FilterTasks.buildTokenSets(STATE.taskmap);
  renderView();
}

function removeQueue(id) {
  delete STATE.queuemap[id];
  removeEle(STATE.queues, id);
  renderView();
}

function addQueue(queue) {
  STATE.queues.push(queue.id);
  STATE.queuemap[queue.id] = queue;
  renderView();
}

function removeEle(list, ele) {
  var index = list.indexOf(ele);
  if (index > -1) {
    list.splice(index, 1);
  }
}

function putTaskInQueue(taskId, queueName) {
  var currentQueue = STATE.taskmap[taskId].queue

  if (currentQueue && STATE.queuemap[currentQueue]) {
    removeEle(STATE.queuemap[currentQueue].tasks, taskId)
    }
  STATE.taskmap[taskId].queue = queueName;
  if (queueName && STATE.queuemap[queueName]) {
    STATE.queuemap[queueName].tasks.push(taskId);
  }
  renderView();

  $.ajax({
    url: '/task/' + taskId  + '/update/' + 'queue/' + queueName,
    type: 'POST'
  });
}

function renderView() {
  /*
   * Render HTML from the state and put on the DOM
   */
  $('#org-selector').html(TEMPLATES['org-selector'](STATE.orgs));
  var selectedQueues = _.filter(STATE.queues, function(queueId) {
    return STATE.queuemap[queueId].selected;
  });


  renderSavedFilters();

  var taskViewHTML = '';
  if (selectedQueues.length) {
    _.each(selectedQueues, function(queueId) {
      taskViewHTML += renderQueueTasks(queueId);
    });
  } else {
    taskViewHTML = renderQueueTasks();
  }
  var queueHTML = _.map(STATE.queues, function(queueId) {
    return TEMPLATES['queue-row'](STATE.queuemap[queueId]);
  });
  queueHTML = queueHTML.join('');

  var createTaskHTML = TEMPLATES['create-task']({visible: STATE.showingCreateTask});
  var allTaskHTML = createTaskHTML + taskViewHTML;
  $('#task-view').html(allTaskHTML);


  $('#queue-list').html(queueHTML);


  $('.tasks-table').dataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bFilter": false,
        "bSort": false,
        "bInfo": false,
        "bAutoWidth": false 
  });
  $('.tasks-table tbody tr').click(function(ev) {
    //Stop the details section from opening when selecting stuff
    if ($(ev.target).is('select') ) {
      return false
    }
    var tasksTable = $('.tasks-table').dataTable();
    if (tasksTable.fnIsOpen(this)) {  
      tasksTable.fnClose( this );
    }    
    else {  
      var taskId = $(this).attr('id');
      tasksTable.fnOpen( this, TEMPLATES['task-details']({task: STATE.taskmap[taskId]}), 'task-details');  
    }
  });
  /* 
   * Hook up any needed event handlers
   */

  $( ".create-form-container button[type='submit']" ).on('click',  function( event ) {
    var formData = $(this).parent('form').serialize();
    $.ajax({
      url: '/task',
      type: 'POST',
      data: formData,
      success: function(data) {
        addTask(data);
      }
    });

    return false;
  });
  $('.create-task-close').click(function() {
    $('.create-form-container').toggleClass('hidden');
    STATE.showingCreateTask = !STATE.showingCreateTask;
  });
  $('.task-tags').select2({
    placeholder: "Add a tag",
    tags: STATE.tags
  }).change(function(val) {
    var tags = val.val;
    var taskId = $(this).data('task-id');
    $.ajax({
      url: '/task/' + taskId + '/tags/',
      type: 'POST',
      data: {
        tags: JSON.stringify(tags)
      },
      success: function() {
        STATE.taskmap[taskId].tags = tags.join(',');
        newTags = _.difference(tags, STATE.tags);
        STATE.tags = STATE.tags.concat(newTags);
        FilterTasks.buildTokenSets(STATE.taskmap);
      }
    });
  });
  $('#task-view tbody').sortable({
    items: '.task-row',
    cursorAt: { left: 5, top: 5 },
    helper: function(e, ui) {
      var text = STATE.taskmap[ui.prop('id')].name;
      return $('<div class="dragged-task">' + text + '</div>');
    },
    stop: function(e, ui) {
      var queueName = $(this).parent('table').data('queue-name');

      if (ui.item.data('justDropped')) {
        // Don't have a nicer way of doing this, prevents sorting behavior if we've
        // ended the drag by dropping the task into another queue
        ui.item.data('justDropped', false);
        return false;
      }

      var tasks = $(this).sortable('toArray', {attribute: 'id'});

      if (queueName) {
        reorderList(tasks, STATE.queuemap[queueName].tasks, '/order/task/' + queueName);
        STATE.queuemap[queueName].tasks = tasks;
      } else {
        reorderList(tasks, STATE.tasks, '/order/task/');
        STATE.tasks = tasks;
      }
    }
  });

  $('#task-view table').droppable({
    accept: function(taskRow) {
      // Don't allow dropping into the queue it's already in
      var queueName = $(this).data('queue-name');
      return queueName && ($(this).data('queue-name') !== taskRow.data('queue-name'));
    },
    drop: function(e, ui) {
      var taskId = ui.draggable.prop('id');
      var queueName = $(this).data('queue-name');
      putTaskInQueue(taskId, queueName);

      ui.draggable.data('justDropped', true);
    },
    hoverClass: 'drop-hover'
  });

  $('.queue-row').droppable({
    drop: function(e, ui) {
      var queueName = $(this).data('queue-id');
      var taskId = ui.draggable.prop('id');
      if (!taskId) {
        return false;
      }
      if (STATE.taskmap[taskId].queue !== queueName) {
        putTaskInQueue(taskId, queueName);
      }

      ui.draggable.data('justDropped', true);
    },
    hoverClass: 'drop-hover'
  });

  saveCookies();
}

function renderQueueTasks(queueId) {
  // Default to ALL if no queueId given
  var tasks = queueId ? STATE.queuemap[queueId].tasks : STATE.tasks;
  var searchString = STATE.searchString;

  var selectedFilters = [];
  _.each(STATE.filtermap, function(filter) {
    if (filter.selected) {
      selectedFilters.push(filter.compiled);
    }
  });
  selectedFilters.push(FilterTasks.compileFilter(searchString));

  var taskHTML = _.map(tasks, function(taskId) {
    var task = STATE.taskmap[taskId];

    if (task) {
      var matched = _.every(selectedFilters, function(filter) {
        return filter.match(task);
      });

      if (matched) {
        var context = $.extend({
          cssClass: ''
        }, task);

        _.each(styleRules, function(styleRule) {
          if (styleRule.filter.match(context)) {
            context.cssClass = styleRule.cssClass;
          }
        });

        return TEMPLATES['task-row'](context);
      }
    }

    return '';
  });
  taskHTML = taskHTML.join('');

  return TEMPLATES['task-list']({queueName: queueId, tasks: taskHTML});
}

function renderSavedFilters() {

  var filter_names = _.keys(STATE.filtermap);
  filter_names.sort();

  var filterHTML =_.map(filter_names, function(name) {
    var filter = _.clone(STATE.filtermap[name]);
    filter.rule = filter.rule.replace(/"/g, '&quot;');
    return TEMPLATES['saved-filter'](filter);
  });

  $('#saved-filters').html(filterHTML.join(''));
}

function saveCookies() {
  /*
   * Save current view, selected filters, queues, etc.
   */
  var selectedQueues = [];
  _.each(STATE.queuemap, function(queue) {
    if (queue.selected) {
      selectedQueues.push(queue.id);
    }
  });

  var selectedFilters = [];
  _.each(STATE.filtermap, function(filter) {
    if (filter.selected) {
      selectedFilters.push(filter.name);
    }
  });

  var view = {
    selectedQueues: selectedQueues,
    selectedFilters: selectedFilters,
    searchString: STATE.searchString
  };

  $.cookie(COOKIES.view, JSON.stringify(view));
}

function loadCookies() {
  var view = $.cookie(COOKIES.view);
  try {
    if (view) {
      view = JSON.parse(view);
      _.each(view.selectedQueues, function(queueId) {
        var queue = STATE.queuemap[queueId];
        if (queue) {
          queue.selected = true;
        }
      });

      _.each(view.selectedFilters, function(filterName) {
        var filter = STATE.filtermap[filterName];
        if (filter) {
          filter.selected = true;
        }
      });

      if (view.searchString) {
        STATE.searchString = view.searchString;
        $('#filter-tasks').val(view.searchString);
      }
    }
  } catch(err) {
    // Remove invalid cookies
    $.removeCookie(COOKIES.view);
  }
}

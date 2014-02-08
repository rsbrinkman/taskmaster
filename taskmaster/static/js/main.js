var TEMPLATES = {}
var WHITESPACE = new RegExp(/\s+/);

$(function() {
  loadTemplates()

  // Used for quick filtering, need to call everytime we add/remove tokens to a task
  FilterTasks.buildTokenSets(STATE.taskmap);
  
  renderView();
  setEventHandlers();
});

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
    $.ajax({
      url: '/task/' + taskId  + '/update/' + 'queue/' + queue,
      type: 'POST',
      success: function() {
        var currentQueue = STATE.taskmap[taskId].queue
        if (currentQueue) {
          removeEle(STATE.queuemap[currentQueue].tasks, taskId)
          }
        STATE.taskmap[taskId].queue = queue;
        if (queue) {
          STATE.queuemap[queue].tasks.push(taskId);
        }
        renderView();
      }
    });
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

  $('.container').on('change', '#task-description', function() {
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
      type: 'POST',
      success: function() {
        STATE.taskmap[taskId].status = status;
      }
    });
  });

  $('.create-tasks').click(function() {
    $('.create-form-container').toggleClass('hidden');
  });

  $( "#create-task-form" ).submit(function( event ) { 
    event.preventDefault();
    var formData = $(this).serialize();
    $.ajax({
      url: '/task',
      type: 'POST',
      data: formData,
      success: function(data) {
        addTask(data);
      }
    });
  });

  $('#filter-tasks').keyup(function() {
    renderView();
  });

  $('#queue-list').sortable({
    stop: function(e, ui) {
      var queues = $(this).sortable('toArray', {attribute: 'data-queue-id'});

      // Check if the order has changed
      if(JSON.stringify(STATE.queues) !== JSON.stringify(queues)) {
        // Generate a list of [new_position1, queue1, new_position2, queue2, ...]
        var updates = [];
        _.each(STATE.queues, function(queueName, index) {
          if (queueName !== queues[index]) {
            updates.push(queues.indexOf(queueName));
            updates.push(queueName);
          }
        });

        $.ajax({
          type: 'PUT',
          url: '/order/queue/',
          data: {
            updates: JSON.stringify(updates)
          }
        });

        STATE.queues = queues;
      }
    }
  });
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

function renderView() {
  /*
   * Render HTML from the state and put on the DOM
   */
  var selectedQueues = _.filter(STATE.queues, function(queueId) {
    return STATE.queuemap[queueId].selected;
  });
  

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
  
  var createTaskHTML = TEMPLATES['create-task']('');
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
}

function renderQueueTasks(queueId) {
  // Default to ALL if no queueId given
  var tasks = queueId ? STATE.queuemap[queueId].tasks : STATE.tasks;
  var filterTokens;
  var searchString = $('#filter-tasks').val();
  if (searchString) {
    filterTokens = searchString.trim().toLowerCase().split(WHITESPACE);
  }

  var taskHTML = _.map(tasks, function(taskId) {
    if (jQuery.isEmptyObject(filterTokens)) {
      return TEMPLATES['task-row'](STATE.taskmap[taskId]);
    }
    else if (FilterTasks.isAccepted(taskId, filterTokens)) {
      return TEMPLATES['task-row'](STATE.taskmap[taskId]);
    } else {
      return '';
    }
  });
  taskHTML = taskHTML.join('');


  return TEMPLATES['task-list']({queueName: queueId, tasks: taskHTML});
}

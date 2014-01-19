$(function() {
  $('.task-tags').select2({
    placeholder: "Add a tag",
    tags: TAGS.split(',')
  }).change(function(val) {
    $.ajax({
      url: '/task/' + $(this).data('tag-id') + '/tags/',
      type: 'POST',
      data: {
        tags: JSON.stringify(val.val)
      }
    });
  });
});

$(function() {
    $('.delete-queue').click(function() {
        var id = $('.delete-queue').data('id');
        $.ajax({
            url: '/queue/' + id,
            type: 'DELETE',
            success: removeQueue
        });
    function removeQueue(result) {
        $('#' + id).remove();
    }
    });
});

$(function createQueue() {
    $('#create-queue').click(function(){
        var queue = $('#queue-name').val();
        $.ajax({
          url: '/queue/' + queue,
          type: 'POST',
          success: addQueue
        });  
    function addQueue(result) {
       $('#queue-list').append('<li id=' + queue + '><a href="#" class="delete-queue" data-id=' + queue + '>x</a> ' + queue +'</li>');
    }
    });
});

$('#queue-name').keyup(function(ev) {
    if (ev.which == 13) {
        createQueueKeyUp($('#queue-name').val());
    }   
});

function createQueueKeyUp(queue) {
    $.ajax({
          url: '/queue/' + queue,
          type: 'POST',
          success: addQueue
        });  
    function addQueue(result) {
       $('#queue-list').append('<li id=' + queue + '><a href="#" class="delete-queue" data-id=' + queue + '>x</a> ' + queue +'</li>');
    }
};


$(function() {
    $('#task-status').change(function() {
        var status = $('#task-status').val();
        var taskId = $('#task-status').data('task-id');
        $.ajax({
          url: '/task/' + taskId  + '/update/' + 'status/' + status,
          type: 'POST'
        });
    });
});


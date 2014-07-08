  $('#search').click(function () {
    var org = $('#org-search').val();
    $.ajax({
      type: 'POST',
      url: '/orgs/' + org,
      success: function(data) {
        // display the results
        if (!data) {
            $('.search-results').empty()
            $('.search-results').append('No Search results found');
        }
        else {
            $('.search-results').empty()
            $('.search-results').append(data.name + '<button data-org-id="' + data.id + '" data-org-name="' + data.name + '" class="btn btn-sm join-org">Join</button>');
        }

      }
    });
  });


  $('#search-button').click(function (ev) {
    var org = $('#org-search').val();
    $.ajax({
      type: 'POST',
      url: 'search/orgs/?term=' + org,
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


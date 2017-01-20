$('#postDeleteModal').on('show.bs.modal', function (event) {

    var button = $(event.relatedTarget);
    var postID = button.data('postid');
    var modal = $(this);

    var url = `/api/posts/${postID}`;

    fetch(url).then(r => r.json()).then(data => {

        modal.find('.modalPostTitle').text(data.title);
        modal.find('.modalPostAuthor').text(data.author);

        var url = `/posts/delete/${data.slug}`;
        modal.find('#postDeleteForm').attr('action', url);

    });

});

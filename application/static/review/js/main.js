function toggleTable(e) {
    const id = $(e).attr('toggle');
    $(`.team-body[name=${id}]`).slideToggle('fast');
    $(e).parent().children('.reviewer-actions').fadeToggle('fast');
    if ($(e).attr('toggle-closed') === 'true') {
        $(e).children('span').text('–');
        $(e).attr('toggle-closed', 'false');
    } else {
        $(e).children('span').text('+');
        $(e).attr('toggle-closed', 'true');
    }
}




function update(id, type, data) {
    /*
    `id` is the identifier for either a team (team code) or user (uuid)
    `type` is one of "team" or "user"
    `data` is an object whose keys are database columns and value what to update
    Example:
        data = {
            status: "accepted",
            evaluator_comments: "This team is really great",
            interest: 10,
            experience: 7,
            quality: 9
        }
    Not all database columns need to be set
    */
    console.log(id, type, data);

    if (data.hasOwnProperty("status")) {
        if (type === "user") {
            $(`tr[data-uid=${id}]`)
                .find(".status")
                .html(data.status)
                .removeClass()
                .addClass("status")
                .addClass(data.status);
        } else if (type === "team") {
            $(`tbody[data-team=${id}]`)
                .find(".status")
                .html(data.status)
                .removeClass()
                .addClass("status")
                .addClass(data.status);
        }
    }

}

function addFeedback(id, type) {
    /*
    `id` is the identifier for either a team (team code) or user (uuid)
    `type` is one of "team" or "user"
    */
    let serializedForm = $(`form[id=feedback-${id}]`).serializeArray();
    let data = {};
    for (let i of serializedForm) {
        data[i.name] = i.value;
    }
    update(id, type, data);
}


function toggleTable(e) {
    const id = $(e).attr('toggle');
    $(`.team-body[data-id=${id}]`).slideToggle('fast');
    $(e).parent().children('.reviewer-actions').fadeToggle('fast');
    if ($(e).attr('toggle-closed') === 'true') {
        $(e).children('span').text('–');
        $(e).attr('toggle-closed', 'false');
    } else {
        $(e).children('span').text('+');
        $(e).attr('toggle-closed', 'true');
    }
}

function setUserStatus(uuid, status) {
    $(`tr[data-uid=${uuid}]`)
        .find(".status")
        .html(status)
        .removeClass()
        .addClass("status")
        .addClass(status);
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

    //TODO: Make URL dynamic depending on environment
    if (type === "team") {
        $.ajax({
            method: "PATCH",
            url: `/api/teams/${id}/`,
            contentType: "application/json",
            data: JSON.stringify(data),
        })
            .done(response => {
                for (let user of response.members) {
                    setUserStatus(user.uuid, user.status);
                }
            })
            .fail((jqXHR, textStatus) => {
                alert("Something went wrong. Let the webmasters know.");
                console.log(jqXHR);
                console.log(textStatus);
            });
    } else if (type === "user") {
        $.ajax({
            method: "PATCH",
            url: `/api/users/${id}/`,
            contentType: "application/json",
            data: JSON.stringify(data),
        })
            .done(response => {
                setUserStatus(response.uuid, response.status)
            })
            .fail((jqXHR, textStatus) => {
                alert("Something went wrong. Let the webmasters know.");
                console.log(jqXHR);
                console.log(textStatus);
            });
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


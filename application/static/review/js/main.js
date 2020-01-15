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


function setStatus(e, status) {
    console.log(status)
}
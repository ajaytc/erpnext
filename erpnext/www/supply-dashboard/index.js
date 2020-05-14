$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
    $('.item').css('cursor', 'pointer')
    $('.item').click(function () {
        let ref = $(this).data('ref')
        {% if isFabric %}
        let prefix = '/fabric-summary'
        {% elif isTrimming %}
        let prefix = '/trimming-summary'
        {% elif isPackaging %}
        let prefix = '/packaging-summary'
        {% endif %}

        window.location.href = `${prefix}?order=${ref}`
    })
})
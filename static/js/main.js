var cur_url = window.location.href;
function showConfigFile(){

    var ajax_obj = $.ajax({
        url: cur_url+"read_config_file/",
        type: "POST",
        async: false,
        error: function(xhr, errmsg, err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
    var result = ajax_obj.responseText; 
    $('.config_content').text(result);
    $('.config_content').css('height','1px');
    var scrollHeight = $('.config_content').get(0).scrollHeight;
    $('.config_content').css('height', (25+scrollHeight)+'px');
}

function sniff_type_select_event_handler() {
    $(".sniff_type").change(function() {
        var sniff_type = $(this).find('option:selected').val();
        if (sniff_type == 'realtime') {
            console.log('realtime');
            $('.form-group-input-file').addClass('hidden');
            $('.form-group-log-file').removeClass('hidden');
            $('.container-attenuator').removeClass('hidden');
            $('.form-group-interface').removeClass('hidden');
            $('.result-block > p').empty();
            $('#result_block').addClass('hidden');
        } else {
            console.log('file');
            $('.form-group-input-file').removeClass('hidden');
            $('.form-group-log-file').addClass('hidden');
            $('.container-attenuator').addClass('hidden');
            $('.form-group-interface').addClass('hidden');
            $('.result-block > p').empty();
            $('#result_block').addClass('hidden');
        }
    });
}

function check_input() {
    var sniff_type = $('.sniff_type').find('option:selected').val();
    if (sniff_type == 'realtime') {
        if ($('input.interface').val() == '' ||
            $('select.mode').val() == '' ||
            $('input.dev').val() == '') {
            alert('Interface, mode, dev cat not by empty');
            return;
        }
        send_data('');
    } else {
        var file = document.getElementById('filebutton').files[0];
        if (typeof(file) == 'undefined') {
            alert('input file can not be empty.');
            return;
        }
        readBlob(file);
    }
}

function readBlob(file) {

    console.log('in readBlob');

    var reader = new FileReader();

    reader.onloadend = function(evt) {
        if (evt.target.readyState == FileReader.DONE) {
            console.log('read done');
            send_data(evt.target.result);
        }
    };
    reader.readAsBinaryString(file);
    console.log('leave readBlob');
}

function readConfigFile() {

    var file = document.getElementById('configfilebutton').files[0];
    console.log('in readConfigFile');

    var reader = new FileReader();

    reader.onloadend = function(evt) {
        if (evt.target.readyState == FileReader.DONE) {
            console.log('read done');
            $('.config_content').text(evt.target.result);
            $('.config_content').css('height','1px');
            var scrollHeight = $('.config_content').get(0).scrollHeight;
            $('.config_content').css('height', (25+scrollHeight)+'px');

            $('#saveconfigbutton').removeClass('hidden');
        }
    };
    reader.readAsBinaryString(file);
    console.log('leave readBlob');
}

function saveConfigFile(){
    var file_content = $('.config_content').text();
    //info_dict = JSON.stringify(info_dict);

    var ajax_obj = $.ajax({
        url: cur_url+"save_config_file/",
        type: "POST",
        async: false,
        data: { file_content:file_content },
        error: function(xhr, errmsg, err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
                " <a href='#' class='close'>&times;</a></div>");
            console.log(xhr.status + ": " + xhr.responseText); 
        }
    });
    $('#saveconfigbutton').addClass('hidden');
    alert('Your config is saved.');
}

function handleFileSelect(evt) {
    console.log('in handleFileSelect');
    var file = evt.target;
    var startByte = '0';
    var endByte = file.size;
    readBlob(startByte, endByte, file);
}

function send_data(file_content) {

    console.log('in send_data');

    var sniff_type = $('.sniff_type').find('option:selected').val();
    var info_dict = {};

    if (sniff_type == 'realtime') {
        info_dict['sniff_type'] = $('select.sniff_type').val();
        info_dict['interface'] = $('input.interface').val();
        info_dict['log'] = $('input.log').val() ? $('input.log').val() : 'sniff.log';
        info_dict['mode'] = $('select.mode').val();
        info_dict['dev'] = $('input.dev').val();
    } else {
        info_dict['sniff_type'] = $('select.sniff_type').val();
        info_dict['input_content'] = file_content;
    } 

    console.log(info_dict);
    info_dict = JSON.stringify(info_dict);

    var ajax_obj = $.ajax({
        url: cur_url+"work/",
        type: "POST",
        async: false,
        data: { info_dict: info_dict },
        error: function(xhr, errmsg, err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
    var result = ajax_obj.responseText; 
    result = result.replace(/(?:\r\n|\r|\n)/g, '<br />');
    htmlResult = $.parseHTML(result);
    $('.result-block > p').append(htmlResult);
    console.log(htmlResult);
    $('#result_block').removeClass('hidden');

};
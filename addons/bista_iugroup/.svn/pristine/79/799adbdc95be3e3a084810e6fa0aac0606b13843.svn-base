/*global $, document*/


session_id = "";
var uniq_id_counter = 0;

erp_url = "http://192.168.1.137:8069"
erp_db = "iug_new"
user = "admin"
pass = "admin"

/*
 * GENERIC FUNCTION FOR JSON/AJAX
 */


/** Formats an AJAX response to wrap JSON.
 */
function rpc_jsonp(url, payload) {

     "use strict";

    // extracted from payload to set on the url
    var data = {
        session_id: session_id,
        id: payload.id
    };

    var ajax = {
        type: "POST",
        dataType: 'jsonp',
        jsonp: 'jsonp',
        cache: false,
        data: data,
        url: url
    };

    var payload_str = JSON.stringify(payload);
    var payload_url = $.param({r: payload_str});
    if (payload_url.length < 2000) {
//         throw new Error("Payload is too big.");
    }
    // Direct jsonp request
//     debugger;
    console.log(ajax);
    ajax.data.r = payload_str;
    console.log(ajax);
    return $.ajax(ajax);

}

/** Formats a standard json 2.0 call
 */
function json(url, params) {

     "use strict";

    var deferred = $.Deferred();

    uniq_id_counter += 1;
    var payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': params,
        'id': ("r" + uniq_id_counter)
    };

    rpc_jsonp(url, payload).then(function (data, textStatus, jqXHR) {
        if (data.error) {
            deferred.reject(data.error);
        }
        deferred.resolve(data.result, textStatus, jqXHR);
    });
    return deferred;
}

/*
 * OpenERP functions
 */

function login() {

    "use strict";
    var deferred = $.Deferred();
    
    json(erp_url +'/web/session/authenticate', 
	 {
        'base_location': erp_url,
        'db': erp_db,
        'login': user,
        'password': pass ,
        'session_id': session_id
    }).done(function (data) {
      
         session_id = data.session_id;
        deferred.resolve();
    });

    return deferred;
}

function get_event(event_id) {
    console.log("get event")
    console.log(event_id)
//    var event_id = getParameterByName('id');
    "use strict";
    if (event_id != null){
        json(erp_url + '/web/dataset/search_read',
             {"model":"event","fields":["name","id"],"domain":[["id","=",event_id]],"context":{"uid":1},"session_id":session_id}
        
        ).then(function (data) {
          console.log(data)
          if(data.records.length){
            $('#event_number').html(data.records[0].name);
          }
          else
          {
               $('#error_wrapper').css('display','block');
               $('#event_wrapper').css('display','none');
               $('#event_verify_wrapper').css('display','none');
               $('#event_update_wrapper').css('display','none');
               $('#event_update_msg_wrapper').css('display','none');
               $('#event_verify_msg_wrapper').css('display','none');

          }
        }).fail(function (error) {
                $('#error_wrapper').css('display','block');
                $('#event_wrapper').css('display','none');
                $('#event_verify_wrapper').css('display','none');
                $('#event_update_wrapper').css('display','none');
                $('#event_update_msg_wrapper').css('display','none');
                $('#event_verify_msg_wrapper').css('display','none');

        });
     }
     else{
         alert('arguements not passed')
        $('#error_wrapper').css('display','block');
        $('#event_wrapper').css('display','none');
        $('#event_verify_wrapper').css('display','none');
        $('#event_update_wrapper').css('display','none');
        $('#event_update_msg_wrapper').css('display','none');
        $('#event_verify_msg_wrapper').css('display','none');
         
     }
}

function verify_event()
{
    "use strict";
    var event_id = getParameterByName('id');

    json(erp_url + '/web/dataset/call_kw',
     {"model":"event","method":"event_verify","args":[event_id],"kwargs":{},"session_id":session_id,"context":{"lang":"en_US","tz":false,"uid":1}}
    ).then(function (data) {
      if (data == true){
          $('#event_verify_wrapper').css('display','block');
          $('#event_wrapper').css('display','none');
          $('#error_wrapper').css('display','none');
          $('#event_update_wrapper').css('display','none');
          $('#event_update_msg_wrapper').css('display','none');
          $('#event_verify_msg_wrapper').css('display','none');
      }
      else{
          $('#event_verify_msg_wrapper').css('display','block');
          $('#event_wrapper').css('display','none');
          $('#error_wrapper').css('display','none');
          $('#event_verify_wrapper').css('display','none');
          $('#event_update_wrapper').css('display','none');
          $('#event_update_msg_wrapper').css('display','none');

      }
    }).fail(function (error) {
            $('#error_wrapper').css('display','block');
			$('#event_wrapper').css('display','none');
            $('#event_update_msg_wrapper').css('display','None');
            $('#event_verify_wrapper').css('display','none');
            $('#event_update_wrapper').css('display','none');
            $('#event_verify_msg_wrapper').css('display','none');
            
     });
}

function update_event()
{
    console.log("Update Event")
    "use strict";
    var event_id = getParameterByName('id');
    alert("update "+ event_id);
    var date1 = $("#datepicker").val();
    var time1 = $("#timepicker").val();
    var date2 = $("#datepicker").val();
    var time2 = $("#timepicker2").val();
    
    json(erp_url + '/web/dataset/call_kw',
     {"model":"event","method":"event_update","args":[ event_id ],"kwargs":{},"session_id":session_id,"context":{"lang":"en_US","tz":false,"uid":1}}
    ).then(function (data){
      console.log("update event")
      console.log(data)
      alert(data)
      if (data == true){
          alert('Event Verified succesfully!')
          $('#event_update_wrapper').css('display','block');
          $('#event_wrapper').css('display','none');
          $('#error_wrapper').css('display','none');
          $('#event_verify_wrapper').css('display','none');
          $('#event_update_msg_wrapper').css('display','none');
          $('#event_verify_msg_wrapper').css('display','none');
      }
      else{
          $('#event_update_msg_wrapper').css('display','block');
          $('#event_wrapper').css('display','none');
          $('#error_wrapper').css('display','none');
          $('#event_verify_wrapper').css('display','none');
          $('#event_update_wrapper').css('display','none');
          $('#event_verify_msg_wrapper').css('display','none');
      }

    }).fail(function (error) {
        console.log("Error")
        console.log(error)
        $('#error_wrapper').css('display','block');
        $('#event_update_msg_wrapper').css('display','none');
        $('#event_wrapper').css('display','none');
        $('#event_verify_wrapper').css('display','none');
        $('#event_update_wrapper').css('display','none');
        $('#event_verify_msg_wrapper').css('display','none');
     });
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
        console.log(results)
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function validate()
{
   if( $('#datepicker').val() == "" )
   {
     alert( "Please enter date!" );
     $('#datepicker').focus() ;
     return false;
   }
   if( $('#timepicker').val() == "" )
   {
     alert( "Please enter from time!" );
     $('#timepicker').focus() ;
     return false;
   }
   if( $('#timepicker2').val() == "" )
   {
     alert( "Please enter to time!" );
     $('#timepicker2').focus() ;
     return false;
   }
   
   
//   update_event();
   return( true );
}

$(document).ready(function() {
    "use strict";
	var event_id = getParameterByName('id');
        alert(event_id)
	login().then(
	function(){
		get_event(event_id);
		//$("#dtBox").DateTimePicker();
	});
	//$( "#datepicker" ).datepicker({
	  //dateFormat: "yy-mm-dd"
	//});
	//$( "#datepicker2" ).datepicker({
	  //dateFormat: "yy-mm-dd"
	//});
	//$('#update_event').click(function(){
		//update_event();
	//});
	$('#verify_event').click(function(){
		verify_event();
	});
	$('#update_event').click(function () {
		// var datepicker = document.getElementById("datepicker").value;
		var startDate = document.getElementById("timepicker").value;
		var endDate = document.getElementById("timepicker2").value;
		// if (!datepicker == '') {
			// alert("Plesae enter Date....");			
		// }
                // else{alert("Plesae enter Date....");}
		// if (!startDate == '') {
						
		// }else{alert("Plesae enter From time....");}
		// if (!endDate == '') {
		// }else{alert("Plesae enter To time....");}
//		console.log("Validate")
                var valid = validate()
//                console.log(valid)
                if (valid == true){

                    update_event();
                }
		if (!endDate == '') {
			if(startDate >= endDate ) {
				alert("From time should be less than End time");
				document.getElementById("timepicker2").value = "";
			}
		}
//		update_event();
	});
});
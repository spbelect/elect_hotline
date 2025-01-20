import {} from 'https://unpkg.com/js-cookie@2.2.1/src/js.cookie.js';
import {} from 'https://cdnjs.cloudflare.com/ajax/libs/jquery.serializeJSON/2.9.0/jquery.serializejson.min.js';

function select2Alpine() {
  this.select2 = $(this.$refs.select).select2();
  this.select2.on("select2:select", (event) => {
    this.selectedCity = event.target.value;
  });
  this.$watch("selectedCity", (value) => {
    this.select2.val(value).trigger("change");
  });
}

window.ufo = {
  url: {
    query: function(query) {
      for (var key in query) { ufo.url.query.params.set(key, query[key]) }
      window.location.search = ufo.url.query.params.toString()
    }
  },
      
  
  client: {
    delete: function(button){
      // Send DELETE request and remove parent element.
      
      var confirm = button.attr('confirm');
      if (confirm && !window.confirm(confirm)) {return}
      
      $.ajax(button.attr('url') || (()=>{throw Error('url required')})(), {method: 'DELETE'})
      .done(function(data){$(button).closest('div,tr').remove()})
    },
    
    
    submit: function(form, data){
      // Submit form.
      // :param: `data` - optional object. If provided, submit only this data, otherwise 
      // submit all serialzed form inputs as json.
      
      var form = $(form);
      var result = form.closest('div').find('div.result')
      var ok = form.closest('div').parent().find('button.primary');
      ok.prop('disabled', true)
      
      return $.ajax({
//         url: $.templates(form.attr('action')).render({modal: form.closest('.modal').data()}),
        url: form.attr('action'),
        method: form.attr('method'),
        data: JSON.stringify(data || form.serializeJSON()),
        error: function(...args) {
          var msg = `<div class='alert alert-danger'>` + ufo.ajax_error_msg(...args) + `</div>`;
//           $.post('https://translate.yandex.net/api/v1.5/tr.json/translate?' + $.param({
//             key: '',
//             text: msg,
//             lang: 'ru'})
//           )
//           .done(function(data){alert(data)})
 
          result.html(msg)
          ok.prop('disabled', false)
        }
      })
      .done(function(data){ 
        result.html(data.message || '')
        ok.prop('disabled', true)
      })
    }
  },
  
  
  ajax_error_msg: function(jqXHR, textStatus, errorThrown) {
    // Return html formatted XHR request error message.
    
    var data = jqXHR.responseJSON;
    if (jqXHR.status == 403) {
      // Возможно CSRF сcookie устарела.
      if(data.detail) {
        return `<div>${jqXHR.status} Произошла ошибка.</div>
        <div>${data.detail}</div>`
      } else {
        return `<div>${jqXHR.status} Произошла ошибка. Попробуйте обновить страницу.</div>`
      }
    }
    if (data && data.status == 'validation error') {
      return `<div>${data.errors}</div>`
    } else if (data && data.detail) {
      return `<div> Произошла ошибка. Уведомление отправлено разработчикам. </div>` +
            `<div>${jqXHR.status} ${errorThrown}</div>` +
            `<div>${data.detail}</div>`
    }
    return `<div> Произошла ошибка. Уведомление отправлено разработчикам. </div>` +
            `<div>${jqXHR.status} ${errorThrown}</div>`
  }
}

ufo.url.query.params = new URLSearchParams(window.location.search);
      

$(function(){
  
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
      }
    },
//       dataType: 'json'
    processData: false,
    contentType: 'application/json; charset=UTF-8',
    error: function(){
      alert($(ufo.ajax_error_msg(...arguments)).get(0).textContent)
    }
  });
  
  $('.accordion').accordion()
  
  $('.dropdown.auto').each(function() {
    var dd = $(this).dropdown('set exactly', ($(this).attr('value') || '').split(','))
    
    dd.dropdown({
      onChange: function (val) {
        if ($(this).attr('onchange')) {
          eval($(this).attr('onchange'))($(this), val)
        }
        dd.dropdown('hide')
      },
      ...eval($(this).attr('params') || '{}'), 
    })
  })
  
  
  $('.modal').modal({
    onVisible: function(){ 
      $(this).find('form').form('validate form') 
      if ($(this).attr('onVisible')) {
        eval($(this).attr('onVisible'))
      }
    },
    onApprove: function() { $(this).find('form').submit(); return false; }
  })
  
  
  $('form.autovalidate').each(function(){
    var form = $(this);
    if ($(this).closest('.modal').get(0)) {
      var okbutton = $(this).closest('.modal').find('button.primary')
    } else {
      var okbutton = $(this).find('button.primary')
    }
    
    this.init = function (){
      var fields = form.find('input,select').get().map(function(x){
        if (x.name && $(x).attr('rules')) {
          return [x.name, {rules: [{type: $(x).attr('rules')}]}]
        } else {
          return []
        }
      })
      
      form.form({
        keyboardShortcuts: false,
        onSuccess: function(){ okbutton.prop('disabled', false) },
        onFailure: function(){ okbutton.prop('disabled', true) },
        fields: Object.fromEntries(fields)
      }).form('validate form')
    }
    
    $(this).on('click', 'button', function() {
      setTimeout(()=>{form.get(0).init()}, 10)
    })
    
    $(this).on('change keyup blur input', 'input,select', function() {
      form.form('validate form');
    });
    
    $(this).on('keypress', 'input', function(e) {
      if(e.which == 13) {
        eval($(e.target).attr('onenter') || '{}')
        return false;
      }
    });
    
    this.init()
  })
})

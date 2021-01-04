let nav_item_a = document.querySelectorAll('a[data-page]');
let save_page = 'posts';
let check = {};
let arr_li = [[]];
let counter = 0;

window.onload = () => {


nav_item_a.forEach((i) => {
    i.addEventListener('click', () => {
        sessionStorage.setItem('save_page', i.dataset.page);
    });
});


if (sessionStorage.getItem('save_page') != null){
    save_page = sessionStorage.getItem('save_page');
}

if (sessionStorage.getItem('save_page') != '') {
    let obj_for_ref = document.querySelector(`a[data-page=${save_page}] > svg`);
    let ref = document.querySelector(`a[data-page=${save_page}]`);

    if (obj_for_ref) {
        obj_for_ref.setAttribute('class', 'active');
    }
    ref.style.color = '#377ba8';
}







check.modal = false;
function check_on_bgModal() {
    if (check.modal) {
        $('.bg_modal').css('display', 'block');
    } else {
        $('.bg_modal').css('display', 'none');
    }
}
function close_modal() {
    $('.modal').css('display', 'none');
    check.modal = false;
    check_on_bgModal();
}

$('.close_modal').click( () => {
    close_modal();
});
$('.bg_modal').click( () => {
    close_modal();
});


document.querySelector(".modal input[name='file_img'][type='file']").addEventListener("change", function () {

    document.querySelector(".modal .prev").innerHTML = '';

    let file = this.files;
    let fr = []

    if (file[0]) {

        for (let i = 0; i < file.length; i++) {

            fr[i] = new FileReader();

            fr[i].addEventListener("load", () => {

                document.querySelector(".modal .prev").innerHTML += `<img src="${fr[i].result}" />`
            }, false);

            fr[i].readAsDataURL(file[i]);
        }


    }
});


function add_Evnt_img() {
    $('img[data-image_open]').click( function () {
        let path_img = this.getAttribute('data-image_open');
        $('.modal.open_img').css('display', 'flex');
        $('.modal.open_img .prev')[0].innerHTML = `<img src="${path_img}" alt="img_modal"/>`;
        check.modal = true;
        check_on_bgModal();
    });
}


$('.wrap_images > ol img').map( (index, item) => {

    if (index % 5 == 0 && index != 0) {
        counter++;
        arr_li.push([]);
        arr_li[counter].push(item);
    } else {

        arr_li[counter].push(item);
    }

    })

    $('.wrap_images > ol').empty();

    arr_li[0].map( (item, index) => {

    $('.wrap_images > ol').append(item);
});


let this_page = 0;
$('.wrap_images .btn_right').click(() => {

    if (arr_li.length != 0 && arr_li.length != 1) {

        $('.wrap_images > ol').empty();

        this_page++;

        if (this_page == arr_li.length) {
            this_page = 0;
        }
        arr_li[this_page].map( (item, index) => {

            $('.wrap_images > ol').append(item);
            add_Evnt_img()
        });
    }
});
$('.wrap_images .btn_left').click(() => {

    if (arr_li.length != 0 && arr_li.length != 1) {

        $('.wrap_images > ol').empty();

        this_page--;

        if (this_page == -1) {

            this_page = arr_li.length-1;
        }
        arr_li[this_page].map( (item, index) => {

            $('.wrap_images > ol').append(item);
            add_Evnt_img()
        });
    }
});

$('[data-modal="upload_img_profile"]').click( () => {
    if (check.modal) {
        $('.modal.upload_img').css('display', 'none');
    } else {
        $('.modal.upload_img').css('display', 'flex');
    }
    check.modal = !check.modal;
    check_on_bgModal();
});

add_Evnt_img();


$('.close_flash').click( () => {

    $('.flash').css('display', 'none');
});
















//end JQuery
}

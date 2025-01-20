
log = console.log;


function equal(x, y) {
    /*
    Deep object comparison.

    Usage:
    >>> x = {1: 2}
    >>> y = {1: 2}

    >>> x == y
    false

    >>> equal(x, y)
    true

    */

    if (x === y) {
        return true;
    }
    else if ((typeof x == "object" && x != null) && (typeof y == "object" && y != null)) {
        if (Object.keys(x).length != Object.keys(y).length)
            return false;

        for (var prop in x) {
            if (y.hasOwnProperty(prop))
            {
                if (! equal(x[prop], y[prop]))
                    return false;
            }
            else
                return false;
        }

        return true;
    }
    else
        return false;
}

// document.addEventListener('DOMContentLoaded', function(){});

document.addEventListener(`click`, function(event){
    // Close choices dropdown on second click.
    if(!event.target.className || !event.target.className.search) return;
    if(event.target.className.search(/choices__inner|is-selected/g) >= 0) {
        div = event.target.closest('.choices.is-open');
        if (div) {
            div.querySelector('select').choices.hideDropdown();
        }
    }
});

daisyChoices = {
    containerOuter: 'choices relative overflow-hidden rounded-lg',
    containerInner: 'choices__inner inline-table px-3 py-0 min-h-1 h-1 select w-full bg-inherit pe-10 cursor-text',
    input: 'choices__input pl-0 inline-block text-sm border-0 ring-0 border-base-300 px-0 py-0 !ring-transparent bg-inherit w-full',
    list: 'choices__list m-0 pl-0 list-none border-0 bg-inherit',
    listItems: 'choices__list--multiple inline-table',
    listDropdown: 'choices__list--dropdown z-[1] absolute px-2 !bg-base-100 lg:px-4 w-full border-1 border-base-300 top-full overflow-auto break-all will-change-auto',
    item: 'choices__item badge badge-primary  rounded-lg mr-1 break-all box-border inline-table',
    itemChoice: 'choices__item--choice cursor-pointer !block !m-auto !my-2 badge-ghost w-full h-auto hover:bg-primary  hover:text-primary-content !text-base bg-base-100 border-none',
    button: 'choices__button -indent-[9999px] h-fit appearance-none border-0 bg-transparent cursor-pointer bg-no-repeat h-2 ml-2 bg-[length:1rem_1rem] hover:bg-[length:1.2rem_1.2rem] opacity-100 bg-center bg-[url("/static/x-mark.svg")] relative inline-block w-4',
    openState: 'overflow-visible',
    disabledState: 'is-disabled bg-base-200 opacity-50',
    // listSingle: 'choices__list--single',
    // itemSelectable: 'choices__item--selectable',
    // itemDisabled: 'choices__item--disabled',
    // description: 'choices__description',
    // placeholder: 'choices__placeholder',
    // group: 'choices__group',
    // groupHeading: 'choices__heading',
    // activeState: 'is-active',
    // focusState: 'is-focused',
    // inputCloned: 'nxx',
    // highlightedState: 'is-highlighted',
    // selectedState: 'is-selected',
    // flippedState: 'is-flipped',
    // loadingState: 'is-loading',
    // notice: 'choices__notice',
    // addChoice: 'choices__item--selectable add-choice',
    // noResults: 'has-no-results',
    // noChoices: 'has-no-choices',
}

// Convert string to list of classes
for (var k in daisyChoices) {
    daisyChoices[k] = daisyChoices[k].split(' ').filter(x => !!x)
}

ufo = {
    // daisyChoices: daisyChoices
    daisyChoices: {}
}

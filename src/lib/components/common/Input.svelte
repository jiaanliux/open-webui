<script lang="ts">
        export let type = 'text';
        export let value: string | number | null | undefined = undefined;
        export let className = '';
        export let id: string | undefined = undefined;
        export let placeholder: string | undefined = undefined;
        export let min: string | number | undefined = undefined;
        export let max: string | number | undefined = undefined;
        export let step: string | number | undefined = undefined;
        export let disabled = false;
        export let name: string | undefined = undefined;
        export let required = false;
        export let readonly = false;
        export let autocomplete: string | undefined = undefined;
        export let inputmode: string | undefined = undefined;
</script>

<input
        {type}
        bind:value
        class={`block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-900 focus-visible:ring-offset-2 placeholder:text-gray-400 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:placeholder:text-gray-500 dark:focus-visible:ring-gray-200 ${className}`}
        {id}
        {placeholder}
        {min}
        {max}
        {step}
        {disabled}
        {name}
        {required}
        {readonly}
        {autocomplete}
        {inputmode}
/>

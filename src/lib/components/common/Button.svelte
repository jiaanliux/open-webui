<script lang="ts">
        type ButtonSize = 'sm' | 'md' | 'lg' | 'icon';
        type ButtonVariant = 'solid' | 'outline' | 'ghost' | 'link';
        type ButtonColor = 'primary' | 'gray' | 'red';

        export let type: 'button' | 'submit' | 'reset' = 'button';
        export let variant: ButtonVariant = 'solid';
        export let size: ButtonSize = 'md';
        export let color: ButtonColor = 'primary';
        export let disabled = false;
        export let className = '';

        const sizeClasses: Record<ButtonSize, string> = {
                sm: 'h-9 px-3 text-sm',
                md: 'h-10 px-4 text-sm',
                lg: 'h-11 px-5 text-base',
                icon: 'h-9 w-9'
        };

        const solidColors: Record<ButtonColor, string> = {
                primary:
                        'bg-gray-900 text-white hover:bg-gray-800 focus-visible:ring-gray-900 dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-white dark:focus-visible:ring-gray-200',
                gray: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus-visible:ring-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 dark:focus-visible:ring-gray-500',
                red: 'bg-red-500 text-white hover:bg-red-600 focus-visible:ring-red-500'
        };

        const outlineColors: Record<ButtonColor, string> = {
                primary:
                        'border border-gray-300 text-gray-900 hover:bg-gray-100 focus-visible:ring-gray-900 dark:border-gray-700 dark:text-gray-100 dark:hover:bg-gray-800 dark:focus-visible:ring-gray-200',
                gray: 'border border-gray-200 text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-400 dark:border-gray-700 dark:text-gray-100 dark:hover:bg-gray-800 dark:focus-visible:ring-gray-500',
                red: 'border border-red-500 text-red-600 hover:bg-red-50 focus-visible:ring-red-500 dark:hover:bg-red-950/40'
        };

        const ghostColors: Record<ButtonColor, string> = {
                primary:
                        'text-gray-900 hover:bg-gray-100 focus-visible:ring-gray-900 dark:text-gray-100 dark:hover:bg-gray-800 dark:focus-visible:ring-gray-200',
                gray: 'text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-400 dark:text-gray-200 dark:hover:bg-gray-800 dark:focus-visible:ring-gray-500',
                red: 'text-red-600 hover:bg-red-50 focus-visible:ring-red-500 dark:hover:bg-red-950/40'
        };

        const linkColors: Record<ButtonColor, string> = {
                primary: 'text-blue-600 hover:underline focus-visible:ring-blue-500 dark:text-blue-400',
                gray: 'text-gray-700 hover:underline focus-visible:ring-gray-400 dark:text-gray-200',
                red: 'text-red-600 hover:underline focus-visible:ring-red-500'
        };

        const variantClasses: Record<ButtonVariant, Record<ButtonColor, string>> = {
                solid: solidColors,
                outline: outlineColors,
                ghost: ghostColors,
                link: linkColors
        };
</script>

<button
        type={type}
        class={`inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${sizeClasses[size]} ${variantClasses[variant][color]} ${className}`}
        {disabled}
>
        <slot />
</button>

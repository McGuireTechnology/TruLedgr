import type { User, UserCreate, UserUpdate } from '@/types';
interface Props {
    user?: User | null;
}
declare const _default: import("vue").DefineComponent<Props, {}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {} & {
    close: () => any;
    save: (data: UserCreate | UserUpdate) => any;
}, string, import("vue").PublicProps, Readonly<Props> & Readonly<{
    onClose?: (() => any) | undefined;
    onSave?: ((data: UserCreate | UserUpdate) => any) | undefined;
}>, {
    user: User | null;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;

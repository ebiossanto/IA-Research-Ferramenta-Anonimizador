// Lean compiler output
// Module: AtratorExtras.Prng
// Imports: Init
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
LEAN_EXPORT lean_object* l_Atrator_splitmixNth___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_deriveSeed(uint64_t, uint64_t, uint64_t);
LEAN_EXPORT lean_object* l_Atrator_splitmixNext___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Atrator_splitmixNext(uint64_t);
uint64_t lean_uint64_of_nat(lean_object*);
LEAN_EXPORT uint64_t l_Atrator_kMix1;
static lean_object* l_Atrator_kMix1___closed__1;
uint64_t lean_uint64_shift_right(uint64_t, uint64_t);
uint64_t lean_uint64_add(uint64_t, uint64_t);
static uint64_t l_Atrator_kSeedB___closed__2;
static lean_object* l_Atrator_kSeedB___closed__1;
uint64_t lean_uint64_mul(uint64_t, uint64_t);
LEAN_EXPORT uint64_t l_Atrator_kGolden;
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
uint64_t lean_uint64_xor(uint64_t, uint64_t);
LEAN_EXPORT lean_object* l_Atrator_splitmixNth(uint64_t, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
static lean_object* l_Atrator_kMix2___closed__1;
static lean_object* l_Atrator_kGolden___closed__1;
LEAN_EXPORT uint64_t l_Atrator_kSeedB;
LEAN_EXPORT lean_object* l_Atrator_deriveSeed___boxed(lean_object*, lean_object*, lean_object*);
static uint64_t l_Atrator_kMix2___closed__2;
static uint64_t l_Atrator_kMix1___closed__2;
static uint64_t l_Atrator_kGolden___closed__2;
LEAN_EXPORT uint64_t l_Atrator_kMix2;
static lean_object* _init_l_Atrator_kGolden___closed__1() {
_start:
{
lean_object* x_1; 
x_1 = lean_cstr_to_nat("11400714819323198485");
return x_1;
}
}
static uint64_t _init_l_Atrator_kGolden___closed__2() {
_start:
{
lean_object* x_1; uint64_t x_2; 
x_1 = l_Atrator_kGolden___closed__1;
x_2 = lean_uint64_of_nat(x_1);
return x_2;
}
}
static uint64_t _init_l_Atrator_kGolden() {
_start:
{
uint64_t x_1; 
x_1 = l_Atrator_kGolden___closed__2;
return x_1;
}
}
static lean_object* _init_l_Atrator_kMix1___closed__1() {
_start:
{
lean_object* x_1; 
x_1 = lean_cstr_to_nat("13787848793156543929");
return x_1;
}
}
static uint64_t _init_l_Atrator_kMix1___closed__2() {
_start:
{
lean_object* x_1; uint64_t x_2; 
x_1 = l_Atrator_kMix1___closed__1;
x_2 = lean_uint64_of_nat(x_1);
return x_2;
}
}
static uint64_t _init_l_Atrator_kMix1() {
_start:
{
uint64_t x_1; 
x_1 = l_Atrator_kMix1___closed__2;
return x_1;
}
}
static lean_object* _init_l_Atrator_kMix2___closed__1() {
_start:
{
lean_object* x_1; 
x_1 = lean_cstr_to_nat("10723151780598845931");
return x_1;
}
}
static uint64_t _init_l_Atrator_kMix2___closed__2() {
_start:
{
lean_object* x_1; uint64_t x_2; 
x_1 = l_Atrator_kMix2___closed__1;
x_2 = lean_uint64_of_nat(x_1);
return x_2;
}
}
static uint64_t _init_l_Atrator_kMix2() {
_start:
{
uint64_t x_1; 
x_1 = l_Atrator_kMix2___closed__2;
return x_1;
}
}
static lean_object* _init_l_Atrator_kSeedB___closed__1() {
_start:
{
lean_object* x_1; 
x_1 = lean_cstr_to_nat("15111065706836454659");
return x_1;
}
}
static uint64_t _init_l_Atrator_kSeedB___closed__2() {
_start:
{
lean_object* x_1; uint64_t x_2; 
x_1 = l_Atrator_kSeedB___closed__1;
x_2 = lean_uint64_of_nat(x_1);
return x_2;
}
}
static uint64_t _init_l_Atrator_kSeedB() {
_start:
{
uint64_t x_1; 
x_1 = l_Atrator_kSeedB___closed__2;
return x_1;
}
}
LEAN_EXPORT lean_object* l_Atrator_splitmixNext(uint64_t x_1) {
_start:
{
uint64_t x_2; uint64_t x_3; uint64_t x_4; uint64_t x_5; uint64_t x_6; uint64_t x_7; uint64_t x_8; uint64_t x_9; uint64_t x_10; uint64_t x_11; uint64_t x_12; uint64_t x_13; uint64_t x_14; uint64_t x_15; uint64_t x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; 
x_2 = l_Atrator_kGolden;
x_3 = lean_uint64_add(x_1, x_2);
x_4 = 30;
x_5 = lean_uint64_shift_right(x_3, x_4);
x_6 = lean_uint64_xor(x_3, x_5);
x_7 = l_Atrator_kMix1;
x_8 = lean_uint64_mul(x_6, x_7);
x_9 = 27;
x_10 = lean_uint64_shift_right(x_8, x_9);
x_11 = lean_uint64_xor(x_8, x_10);
x_12 = l_Atrator_kMix2;
x_13 = lean_uint64_mul(x_11, x_12);
x_14 = 31;
x_15 = lean_uint64_shift_right(x_13, x_14);
x_16 = lean_uint64_xor(x_13, x_15);
x_17 = lean_box_uint64(x_3);
x_18 = lean_box_uint64(x_16);
x_19 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_19, 0, x_17);
lean_ctor_set(x_19, 1, x_18);
return x_19;
}
}
LEAN_EXPORT lean_object* l_Atrator_splitmixNext___boxed(lean_object* x_1) {
_start:
{
uint64_t x_2; lean_object* x_3; 
x_2 = lean_unbox_uint64(x_1);
lean_dec(x_1);
x_3 = l_Atrator_splitmixNext(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* l_Atrator_splitmixNth(uint64_t x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; uint8_t x_4; 
x_3 = lean_unsigned_to_nat(0u);
x_4 = lean_nat_dec_eq(x_2, x_3);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; uint64_t x_7; uint64_t x_8; 
x_5 = lean_unsigned_to_nat(1u);
x_6 = lean_nat_sub(x_2, x_5);
lean_dec(x_2);
x_7 = l_Atrator_kGolden;
x_8 = lean_uint64_add(x_1, x_7);
x_1 = x_8;
x_2 = x_6;
goto _start;
}
else
{
lean_object* x_10; lean_object* x_11; 
lean_dec(x_2);
x_10 = l_Atrator_splitmixNext(x_1);
x_11 = lean_ctor_get(x_10, 1);
lean_inc(x_11);
lean_dec(x_10);
return x_11;
}
}
}
LEAN_EXPORT lean_object* l_Atrator_splitmixNth___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint64_t x_3; lean_object* x_4; 
x_3 = lean_unbox_uint64(x_1);
lean_dec(x_1);
x_4 = l_Atrator_splitmixNth(x_3, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* l_Atrator_deriveSeed(uint64_t x_1, uint64_t x_2, uint64_t x_3) {
_start:
{
uint64_t x_4; uint64_t x_5; uint64_t x_6; uint64_t x_7; uint64_t x_8; uint64_t x_9; lean_object* x_10; lean_object* x_11; 
x_4 = l_Atrator_kGolden;
x_5 = lean_uint64_mul(x_2, x_4);
x_6 = lean_uint64_xor(x_1, x_5);
x_7 = l_Atrator_kSeedB;
x_8 = lean_uint64_mul(x_3, x_7);
x_9 = lean_uint64_xor(x_6, x_8);
x_10 = l_Atrator_splitmixNext(x_9);
x_11 = lean_ctor_get(x_10, 1);
lean_inc(x_11);
lean_dec(x_10);
return x_11;
}
}
LEAN_EXPORT lean_object* l_Atrator_deriveSeed___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint64_t x_4; uint64_t x_5; uint64_t x_6; lean_object* x_7; 
x_4 = lean_unbox_uint64(x_1);
lean_dec(x_1);
x_5 = lean_unbox_uint64(x_2);
lean_dec(x_2);
x_6 = lean_unbox_uint64(x_3);
lean_dec(x_3);
x_7 = l_Atrator_deriveSeed(x_4, x_5, x_6);
return x_7;
}
}
lean_object* initialize_Init(uint8_t builtin, lean_object*);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_AtratorExtras_Prng(uint8_t builtin, lean_object* w) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin, lean_io_mk_world());
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
l_Atrator_kGolden___closed__1 = _init_l_Atrator_kGolden___closed__1();
lean_mark_persistent(l_Atrator_kGolden___closed__1);
l_Atrator_kGolden___closed__2 = _init_l_Atrator_kGolden___closed__2();
l_Atrator_kGolden = _init_l_Atrator_kGolden();
l_Atrator_kMix1___closed__1 = _init_l_Atrator_kMix1___closed__1();
lean_mark_persistent(l_Atrator_kMix1___closed__1);
l_Atrator_kMix1___closed__2 = _init_l_Atrator_kMix1___closed__2();
l_Atrator_kMix1 = _init_l_Atrator_kMix1();
l_Atrator_kMix2___closed__1 = _init_l_Atrator_kMix2___closed__1();
lean_mark_persistent(l_Atrator_kMix2___closed__1);
l_Atrator_kMix2___closed__2 = _init_l_Atrator_kMix2___closed__2();
l_Atrator_kMix2 = _init_l_Atrator_kMix2();
l_Atrator_kSeedB___closed__1 = _init_l_Atrator_kSeedB___closed__1();
lean_mark_persistent(l_Atrator_kSeedB___closed__1);
l_Atrator_kSeedB___closed__2 = _init_l_Atrator_kSeedB___closed__2();
l_Atrator_kSeedB = _init_l_Atrator_kSeedB();
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif

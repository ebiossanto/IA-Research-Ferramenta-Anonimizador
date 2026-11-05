// Lean compiler output
// Module: AtratorCore.Exposure
// Imports: Init AtratorCore.Contraction
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
LEAN_EXPORT lean_object* l_Atrator_rate(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_Atrator_dischargeCeil(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_settleSteps___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_step(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_ceilDiv___boxed(lean_object*, lean_object*);
lean_object* l_Atrator_removal(lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_div(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_disch(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_ceilDiv(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_disch___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_settleStepsFuel___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_step___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_rate___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
lean_object* lean_nat_mul(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_settleSteps(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_boundB___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_boundB(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_settleStepsFuel(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Atrator_rate(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; 
x_5 = lean_nat_dec_lt(x_1, x_4);
if (x_5 == 0)
{
lean_inc(x_2);
return x_2;
}
else
{
lean_inc(x_3);
return x_3;
}
}
}
LEAN_EXPORT lean_object* l_Atrator_rate___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = l_Atrator_rate(x_1, x_2, x_3, x_4);
lean_dec(x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* l_Atrator_disch(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; lean_object* x_7; 
x_6 = l_Atrator_rate(x_2, x_3, x_4, x_5);
x_7 = l_Atrator_dischargeCeil(x_1, x_6, x_5);
lean_dec(x_6);
return x_7;
}
}
LEAN_EXPORT lean_object* l_Atrator_disch___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = l_Atrator_disch(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_5);
lean_dec(x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* l_Atrator_step(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; lean_object* x_8; 
x_7 = lean_nat_add(x_5, x_6);
x_8 = l_Atrator_disch(x_1, x_2, x_3, x_4, x_7);
lean_dec(x_7);
return x_8;
}
}
LEAN_EXPORT lean_object* l_Atrator_step___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = l_Atrator_step(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec(x_6);
lean_dec(x_5);
lean_dec(x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* l_Atrator_ceilDiv(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_3 = lean_unsigned_to_nat(1u);
x_4 = lean_nat_sub(x_2, x_3);
x_5 = lean_nat_add(x_1, x_4);
lean_dec(x_4);
x_6 = lean_nat_div(x_5, x_2);
lean_dec(x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* l_Atrator_ceilDiv___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = l_Atrator_ceilDiv(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* l_Atrator_boundB(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; uint8_t x_12; 
x_6 = lean_nat_sub(x_1, x_3);
x_7 = lean_nat_mul(x_6, x_2);
lean_dec(x_6);
x_8 = l_Atrator_ceilDiv(x_7, x_1);
lean_dec(x_7);
x_9 = lean_nat_sub(x_1, x_4);
x_10 = lean_nat_mul(x_9, x_5);
lean_dec(x_9);
x_11 = l_Atrator_ceilDiv(x_10, x_4);
lean_dec(x_10);
x_12 = lean_nat_dec_le(x_8, x_11);
if (x_12 == 0)
{
lean_dec(x_11);
return x_8;
}
else
{
lean_dec(x_8);
return x_11;
}
}
}
LEAN_EXPORT lean_object* l_Atrator_boundB___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = l_Atrator_boundB(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_5);
lean_dec(x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* l_Atrator_settleStepsFuel(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; uint8_t x_6; 
x_5 = lean_unsigned_to_nat(0u);
x_6 = lean_nat_dec_eq(x_3, x_5);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; uint8_t x_9; 
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_sub(x_3, x_7);
x_9 = lean_nat_dec_eq(x_4, x_5);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_10 = l_Atrator_removal(x_1, x_2, x_4);
x_11 = lean_nat_sub(x_4, x_10);
lean_dec(x_10);
x_12 = l_Atrator_settleStepsFuel(x_1, x_2, x_8, x_11);
lean_dec(x_11);
lean_dec(x_8);
x_13 = lean_nat_add(x_7, x_12);
lean_dec(x_12);
return x_13;
}
else
{
lean_object* x_14; 
lean_dec(x_8);
x_14 = lean_unsigned_to_nat(0u);
return x_14;
}
}
else
{
lean_object* x_15; 
x_15 = lean_unsigned_to_nat(0u);
return x_15;
}
}
}
LEAN_EXPORT lean_object* l_Atrator_settleStepsFuel___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = l_Atrator_settleStepsFuel(x_1, x_2, x_3, x_4);
lean_dec(x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* l_Atrator_settleSteps(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = l_Atrator_settleStepsFuel(x_1, x_2, x_3, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* l_Atrator_settleSteps___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = l_Atrator_settleSteps(x_1, x_2, x_3);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_4;
}
}
lean_object* initialize_Init(uint8_t builtin, lean_object*);
lean_object* initialize_AtratorCore_Contraction(uint8_t builtin, lean_object*);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_AtratorCore_Exposure(uint8_t builtin, lean_object* w) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin, lean_io_mk_world());
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_AtratorCore_Contraction(builtin, lean_io_mk_world());
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif

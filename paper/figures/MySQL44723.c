//ha_myisam.cc
/* don't enable row cache if too few rows */
if (! rows || (rows > MI_MIN_ROWS_TO_USE_WRITE_CACHE) )
    mi_extra(...);
//mi_extra() will allocate write cache 
//and zero-fill write cache
// fix is to remove zero-fill operation
....
// in myisamdef.h:
// #define MI_MIN_ROWS_TO_USE_WRITE_CACHE 10

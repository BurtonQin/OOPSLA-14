notified = false;
while(!notified) {
   rc = pthread_cond_timedwait(
           &cond, &lock, &timeToWait);
   if(rc == ETIMEDOUT) {
      break;
   }
}              

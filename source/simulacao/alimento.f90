program alimento

    implicit none
    integer, parameter :: nr = 60
    integer, parameter :: nh = 30
    real:: dt, Raio, H, ka, rho, Cp, h_convec, epsilon
    real:: sigma, alpha, dr, dh
    integer :: nt, i, j, k, l, m
    real:: T_esteira, T_paredes, T_ar, T_ambiente
    REAL, PARAMETER :: pi = 3.1415927

    real, dimension(nr) :: r
    real, dimension(nh,nr) :: T  ! entrada
    real, dimension(nh,nr) :: Tc

    real :: tf

    tf = 10.0

    dt = 0.05
    Raio = 0.05
    H = 0.01
    ka = 0.1
    rho = 400.0
    Cp = 3000.0
    h_convec = 5.0
    epsilon = 0.7
    T_esteira = 420.0
    T_paredes = 470.0
    T_ar = 450.0
    T_ambiente = 293.0
    sigma = 5.67032e-8
    alpha = ka/(rho*Cp)
    dr = Raio/(nr + 1)
    dh = H/(nh + 1)
    nt = int(tf/dt)



    do i = 1, int(nh)
        do j = 1, int(nr)
            T(i,j) = T_ambiente
            Tc(i,j) = T_ambiente
        enddo
    enddo

    do i = 1, nr
        T(1,i) = T_esteira
        r(i) = i*Raio/nr
    enddo

    do k = 1, nt

        do i = 1, int(nh)
            do j = 1, int(nr)
                Tc(i,j) = T(i,j)
            enddo
        enddo

        do i = 2, int(nh) -1
            do j = 2, int(nr) -1
                T(i,j) = Tc(i,j) + dt*alpha*( &
                (  Tc(i,j+1) - 2*Tc(i,j) + T(i,j-1)  )/dr**2 + &
                ( Tc(i+1,j) - 2*Tc(i,j) + T(i-1,j)  )/dh**2 + &
                ( Tc(i,j+1) - Tc(i,j-1) )/(dr* r(j)) )
            enddo
        enddo

        do i = 1, int(nr)
            T(nh,i) = T(nh-1,i) + dr*epsilon*sigma*(T_paredes**4 - T(nh,i)**4)&
                      + dr*h_convec*( T_ar - T(nh,i))
        enddo

        do i = 1, int(nh)
            T(i,nr) = T(i,nr-1) + dr*epsilon*sigma*(T_paredes**4 - T(i,nr)**4)&
                      + dr*h_convec*( T_ar - T(i,nr))
        enddo

        do i = 1, int(nh)
            T(i,1) = T(i,2)
        enddo

    enddo

    write (*,*) T

end program alimento
